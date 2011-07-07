// lolpy.cpp : Defines the entry point for the console application.
// version 2.0.1
#include <windows.h>
#include <tlhelp32.h>
#include <stdio.h>

typedef HMODULE (WINAPI *pGetModuleHandle)(LPCTSTR);
typedef FARPROC (WINAPI *pGetProcAddress)(HMODULE,LPCSTR);
typedef struct
{
  pGetModuleHandle pfGetModuleHandle;
  pGetProcAddress pfGetProcAddress;
  TCHAR szModule[64];
  CHAR szFunctionName1[64];
  CHAR szFunctionName2[64];
  CHAR szFunctionName3[64];
  const char *code;
} pyfuncs;


 
#pragma check_stack(off) //Needed in debug mode thanks to napalm for helping me fix the debug mode crash...
DWORD WINAPI iCode(pyfuncs *rd)
{
	typedef int (__cdecl *pPyRun_SimpleString)(const char *);
	typedef int (__cdecl *pPy_AddPendingCall)(pPyRun_SimpleString, const char *);
	

	HMODULE hmod = rd->pfGetModuleHandle(rd->szModule);
	if(!hmod)
		return 1;

	pPyRun_SimpleString PyRun_SimpleString = (pPyRun_SimpleString)rd->pfGetProcAddress(hmod, rd->szFunctionName1);
	pPy_AddPendingCall Py_AddPendingCall = (pPy_AddPendingCall)rd->pfGetProcAddress(hmod, rd->szFunctionName2);
	if(!PyRun_SimpleString || !Py_AddPendingCall)
		return 2;

	Py_AddPendingCall(PyRun_SimpleString, rd->code);
	return 0;
}
void __declspec(naked) __stdcall iCodeEnd(){ } //This is the limiter, which we will later need to determine the size
#pragma check_stack(on)//-""-
 


BOOL InjectProcess(HANDLE hProcess, void *func, void *limiter,const char* python_code) 
{
	
	LPVOID lpAddr = 0;
	LPVOID prmAddr = 0;
	DWORD apiAddr = 0;
	HANDLE hRemoteThread = 0;
	DWORD dwSize;
	DWORD *cx;
	DWORD strctSize = sizeof(pyfuncs);
	pyfuncs arg;
	DWORD temp;
	

	cx = (DWORD*) func; //the function addresses are not changed
	dwSize = (DWORD)((DWORD)limiter - (DWORD)cx); //subtract the function from the limiter to obtain the function's size
	arg.code = (const char*)   VirtualAllocEx (hProcess, 0, strlen (python_code) + 1, MEM_COMMIT, PAGE_READWRITE);
	WriteProcessMemory (hProcess, (void *) arg.code, (void *) python_code,
						strlen (python_code) + 1, &temp);

	HMODULE hModule = LoadLibrary("kernel32.dll");
	arg.pfGetModuleHandle = (pGetModuleHandle) GetProcAddress(hModule,"GetModuleHandleA");
	arg.pfGetProcAddress = (pGetProcAddress) GetProcAddress(hModule,"GetProcAddress");
	strcpy(arg.szModule,"python27");
	strcpy(arg.szFunctionName1,"PyRun_SimpleString");
	strcpy(arg.szFunctionName2,"Py_AddPendingCall");



	//Allocate memory for the function
	lpAddr = VirtualAllocEx(hProcess, NULL, dwSize, MEM_COMMIT, PAGE_EXECUTE_READWRITE);
	if(!lpAddr) {
		CloseHandle(hProcess);
		MessageBox(0, "Couldn't allocate memory!", "Error!", MB_OK | MB_ICONERROR);
		return FALSE;
	}
	//Allocate memory for the functions data
	prmAddr = VirtualAllocEx(hProcess, NULL, strctSize, MEM_COMMIT, PAGE_EXECUTE_READWRITE);
	if(!prmAddr) {
		VirtualFreeEx(lpAddr, lpAddr, 0, MEM_RELEASE);
		CloseHandle(hProcess);
		MessageBox(0, "Couldn't allocate memory!", "Error!", MB_OK | MB_ICONERROR);
		return FALSE;
	}
	//Copy the function
	WriteProcessMemory(hProcess, lpAddr, cx, dwSize, NULL);
	//Copy the data
	WriteProcessMemory(hProcess, prmAddr, (LPVOID)&arg, strctSize, NULL);
	//Start the function
	hRemoteThread = CreateRemoteThread(hProcess, NULL, 0,
		(LPTHREAD_START_ROUTINE)lpAddr, prmAddr, 0, NULL);
	if(hRemoteThread) { //If it is successfully created,
		WaitForSingleObject(hRemoteThread, INFINITE); //Wait until it finishes,
		CloseHandle(hRemoteThread); //then close the handle
	}
	VirtualFreeEx(lpAddr, lpAddr, 0, MEM_RELEASE); //Free the memory
	VirtualFreeEx(prmAddr, prmAddr, 0, MEM_RELEASE); //-""-
	return TRUE;
}
 
BOOL InjectCode(char *pName, void *func, void *limiter,const char* python_code)
{

	HANDLE hProcessSnap;
	HANDLE hProcess = NULL;
	PROCESSENTRY32 pEntry32;
 
	ZeroMemory(&pEntry32, sizeof(PROCESSENTRY32));
	pEntry32.dwSize = sizeof(PROCESSENTRY32);
 
	hProcessSnap = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
	if(hProcessSnap == INVALID_HANDLE_VALUE)
		return NULL;
 
	if(!Process32First(hProcessSnap, &pEntry32)) {
		CloseHandle(hProcessSnap);
		return NULL;
	}
	do {
		if(!lstrcmpi(pEntry32.szExeFile, pName)) {	//If the process name matches
			HANDLE hToken;
			LUID luid;
			TOKEN_PRIVILEGES tp;
 
			ZeroMemory(&tp, sizeof(TOKEN_PRIVILEGES));
			if(OpenProcessToken(GetCurrentProcess(), TOKEN_ALL_ACCESS, &hToken)) {
				if(LookupPrivilegeValue(NULL, SE_DEBUG_NAME, &luid)) {
					tp.PrivilegeCount = 1;
					tp.Privileges[0].Luid = luid;
					tp.Privileges[0].Attributes = SE_PRIVILEGE_ENABLED;
					AdjustTokenPrivileges(hToken, FALSE, &tp, sizeof(tp), NULL, NULL); //Try to get debug privileges
				}
				CloseHandle(hToken);
			}
	
			hProcess = OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_OPERATION | PROCESS_VM_WRITE | PROCESS_VM_READ | PROCESS_TERMINATE | PROCESS_CREATE_THREAD
				, FALSE, pEntry32.th32ProcessID); //No matter what open the process
			if(!hProcess) {
				MessageBox(0, "Couldn't open process!", "Error!", MB_OK | MB_ICONERROR);
				return FALSE;
			}
			printf("Processing  eve process %d\n", pEntry32.th32ProcessID);
			InjectProcess(hProcess, func, limiter, python_code);
			CloseHandle(hProcess);//Close the process' handle
		}
	} while(Process32Next(hProcessSnap, &pEntry32));
 
	CloseHandle(hProcessSnap);
	return TRUE; //Succeed.
}


int
main (int argc, char **argv)
{
  HANDLE process_list = CreateToolhelp32Snapshot (TH32CS_SNAPPROCESS, 0);
  PROCESSENTRY32 proc;
  FILE *pyfile;
  int file_size;
  const char *python_code = 0;

  printf("+-------------------------------------------+\n");
  printf("| EVE Python Injector, by pxor128@gmail.com |\n");
  printf("| patched by wibiti, spheremonkey           |\n");
  printf("+-------------------------------------------+\n\n");

  memset (&proc, 0, sizeof (proc));
  proc.dwSize = sizeof (PROCESSENTRY32);

  if (argc != 2)
    {
      printf ("usage: evepy <file>\n");
      exit (0);
    }

  pyfile = fopen (argv[1], "rb");
  if (!pyfile)
    {
      printf ("unable to read file: %s\n", argv[1]);
      exit (0);
    }

  /* Read the python code into memory */
  fseek (pyfile, 0, SEEK_END);
  file_size = ftell (pyfile);
  fseek (pyfile, 0, SEEK_SET);
  python_code = (const char*)calloc (1, file_size+1);
  fread ((void *) python_code, 1, file_size, pyfile);
  fclose (pyfile);

  InjectCode("exeFile.exe", iCode, iCodeEnd, python_code);
  return 0;
}

 
