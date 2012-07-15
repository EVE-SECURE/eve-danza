// lolpy 4
//
#include <windows.h>

#include <Python.h>
#include <pyport.h>
#include <Python-ast.h>
#include <node.h>
#include <grammar.h>
#include <parsetok.h>

#include <marshal.h>

#include <tlhelp32.h>
#include <Psapi.h>
#include <stdio.h>


// i was too lazy to look for proper header for this one
mod_ty (__cdecl PyAST_FromNode)(const node *, PyCompilerFlags *flags,
				  const char *, PyArena *);

//macros to make it easier to add/remove python function ptrs in the injected code
#define LOL_STRUCT(func) decltype(func) *pf##func; CHAR s##func[sizeof(#func)];
#define LOL_SETUP(func) \
	rd->pf##func = (decltype(func) *)rd->pfGetProcAddress(hmod, rd->s##func); \
	if(!rd->pf##func) return 2;
#define LOL_CPYSTR(func) strcpy(arg.s##func, #func);
//the python functions needed in the injected code
#define LOL_LIST(op) \
	LOL_##op(Py_AddPendingCall)\
	LOL_##op(PyEval_EvalCode)\
	LOL_##op(PyEval_GetBuiltins)\
	LOL_##op(PyDict_SetItemString)\
	LOL_##op(Py_DecRef)\
	LOL_##op(PyErr_Occurred)\
	LOL_##op(PyErr_Print)\
	LOL_##op(PyImport_AddModule)\
	LOL_##op(PyModule_GetDict)\
	LOL_##op(PyParser_ParseString)\
	LOL_##op(PyAST_FromNode)\
	LOL_##op(PyArena_New)\
	LOL_##op(PyArena_Free)\
	LOL_##op(PyParser_ParseStringFlagsFilenameEx)\
	LOL_##op(PyNode_Free)\
	LOL_##op(PyAST_Compile)\

#define LC(func) (rd->pf##func)

#define LSTR_STRUCT(strname, strval) char strname[sizeof(strval)]; 
#define LSTR_CPYSTR(strname, strval) strcpy(arg.strname, strval);
//strings we need in the injected code
#define LSTR_LIST(op) \
	LSTR_##op(python27, "python27")\
	LSTR_##op(__main__, "__main__")\
	LSTR_##op(__builtins__, "__builtins__")\
	LSTR_##op(__string__, "<string>")\
	LSTR_##op(__grammar__, "_PyParser_Grammar")

#define LS(strname) (rd->strname)

struct pyfuncs
{
  decltype(GetModuleHandle) *pfGetModuleHandle;
  decltype(GetProcAddress) *pfGetProcAddress;
  decltype(Sleep) *pfSleep;
  LOL_LIST(STRUCT)
  LSTR_LIST(STRUCT)
  grammar *_PyParser_Grammar;
  char *marshalled_code;
  int code_size;
  void *iCallAddress;
  int done;
};


#pragma check_stack(off) //Needed in debug mode thanks to napalm for helping me fix the debug mode crash...
DWORD __cdecl iCode(pyfuncs *rd)
{
	HMODULE hmod = LC(GetModuleHandle)(LS(python27));
	if(hmod == 0)
		return 1;

	LOL_LIST(SETUP)

	if (-1 == LC(Py_AddPendingCall)((int(__cdecl *)(void *))rd->iCallAddress, rd))
		return 3;

	rd->done = -1;
	while (-1 == rd->done)
		LC(Sleep)(100);
	return rd->done;
}

int __cdecl iCall(pyfuncs *rd)
{
	PyCodeObject  *code;
	PyObject *globals, *dum;
    PyCompilerFlags localflags;
    perrdetail err;
    int iflags =    0;
	PyCompilerFlags* flags;
	HMODULE hmod = LC(GetModuleHandle)(LS(python27));
	rd->_PyParser_Grammar =(grammar*) rd->pfGetProcAddress(hmod, LS(__grammar__));
	if (!rd->_PyParser_Grammar) 
		return 4;

	globals = LC(PyModule_GetDict)( LC(PyImport_AddModule)(LS(__main__)) ); //globals = dict of __main__ module
	LC(PyDict_SetItemString)(globals, LS(__builtins__), LC(PyEval_GetBuiltins)()); //add __builtins__ to dict

	PyObject *ret = NULL;
	mod_ty mod;
	PyArena *arena = LC(PyArena_New)();
	if (arena == NULL)
		return 4;

	node *n = LC(PyParser_ParseStringFlagsFilenameEx)(rd->marshalled_code, LS(__string__),
														rd->_PyParser_Grammar, Py_file_input, &err,   &iflags);
	localflags.cf_flags = 0;
	flags = &localflags;
	if (n) {
		flags->cf_flags |= iflags & PyCF_MASK;
		mod = LC(PyAST_FromNode)(n, flags, LS(__string__), arena);
	}

	if (mod != NULL) {
		code = LC(PyAST_Compile)(mod, LS(__string__), flags, arena);
		// process code here.
		if (code != NULL){
			dum = LC(PyEval_EvalCode)(code, globals, globals); //execute code
			LC(Py_DecRef)((PyObject*)code);
			LC(Py_DecRef)(dum);
			if (LC(PyErr_Occurred)()){
				LC(PyErr_Print)(); //prints error to stderr and clears the error
				rd->done = 4;
			} else {
				rd->done = 0;
			}
		}
		else
		{
			rd->done = 4;
		}
	}

	if (n) 
	{
		LC(PyNode_Free)(n);
	}
	if (arena)
	{
		LC(PyArena_Free)(arena);
	}
	rd->done = 0;
	return 0;
}
void __declspec(naked) __stdcall iCodeEnd(){ } //This is the limiter, which we will later need to determine the size
#pragma check_stack(on)//-""-
 

#define SET_ERROR(x) if(sError = (x)) goto error;
BOOL InjectProcess(HANDLE hProcess, char* python_code, int py_code_length)
{	
	LPVOID lpAddr = 0;
	LPVOID prmAddr = 0;
	HANDLE hRemoteThread = 0;
	DWORD dwSize;
	pyfuncs arg;
	LPCSTR sError = NULL;

	dwSize = (DWORD)iCodeEnd - (DWORD)iCode; //subtract the function from the limiter to obtain the function's size
	arg.code_size = py_code_length;
	arg.marshalled_code = (char*)VirtualAllocEx(hProcess, 0, arg.code_size, MEM_COMMIT, PAGE_READWRITE);
	if(arg.marshalled_code == NULL)
		SET_ERROR("Couldn't allocate memory!");

	if(!WriteProcessMemory(hProcess, (void*)arg.marshalled_code, (void*)python_code, arg.code_size, NULL))
		SET_ERROR("Couldn't write memory!");

	HMODULE hModule = LoadLibrary("kernel32.dll");
	arg.pfGetModuleHandle = (decltype(GetModuleHandle) *) GetProcAddress(hModule,"GetModuleHandleA");
	arg.pfGetProcAddress = (decltype(GetProcAddress) *) GetProcAddress(hModule,"GetProcAddress");
	arg.pfSleep = (decltype(Sleep) *) GetProcAddress(hModule,"Sleep");

	LOL_LIST(CPYSTR)
	LSTR_LIST(CPYSTR)
	//Allocate memory for the function
	if(!(lpAddr = VirtualAllocEx(hProcess, NULL, dwSize, MEM_COMMIT, PAGE_EXECUTE_READWRITE)))
		SET_ERROR("Couldn't allocate memory!");
	//Allocate memory for the functions data
	if(!(prmAddr = VirtualAllocEx(hProcess, NULL, sizeof(pyfuncs), MEM_COMMIT, PAGE_EXECUTE_READWRITE)))
		SET_ERROR("Couldn't allocate memory!");
	//Calculate address of iCall in foreign process
	arg.iCallAddress =  (void *) ((DWORD)lpAddr + (DWORD)iCall - (DWORD)iCode);
	//Copy the functions
	if(!WriteProcessMemory(hProcess, lpAddr, (void *)iCode, dwSize, NULL))
		SET_ERROR("Couldn't write memory!");
	//Copy the data
	if(!WriteProcessMemory(hProcess, prmAddr, (LPVOID)&arg, sizeof(pyfuncs), NULL))
		SET_ERROR("Couldn't write memory!");

	//Start the function
	if(!(hRemoteThread = CreateRemoteThread(hProcess, NULL, 0, (LPTHREAD_START_ROUTINE)lpAddr, prmAddr, 0, NULL))) 
		SET_ERROR("Couldn't create remote thread!");

	WaitForSingleObject(hRemoteThread, INFINITE); //Wait until it finishes,

	DWORD iExit = 2;
	GetExitCodeThread(hRemoteThread, &iExit);

	switch(iExit)
	{
	case 1:
		SET_ERROR("python27.dll was null, you tried to inject too early.");
	case 2:
		SET_ERROR("missing export(s).");
	case 3:
		SET_ERROR("Py_AddPendingCall failed.");
	case 4:
		SET_ERROR("Error evaluating code.");
	}

	CloseHandle(hRemoteThread); //then close the handle

	VirtualFreeEx(lpAddr, lpAddr, 0, MEM_RELEASE); //Free the memory
	VirtualFreeEx(prmAddr, prmAddr, 0, MEM_RELEASE); //-""-
	return TRUE;

error:
	MessageBox(NULL, sError, "Error", MB_OK | MB_ICONERROR);
	if(hRemoteThread != NULL)
		CloseHandle(hRemoteThread);
	if(lpAddr != NULL)
		VirtualFreeEx(lpAddr, lpAddr, 0, MEM_RELEASE);
	if(prmAddr != NULL)
		VirtualFreeEx(prmAddr, prmAddr, 0, MEM_RELEASE); 

	return FALSE;
}
 
BOOL InjectCode(char *pName, char* python_code, int code_length)
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
			
			if(InjectProcess(hProcess, python_code, code_length))
				printf("Injection succeeded.\n");
			else
				printf("Injection failed.\n");
			CloseHandle(hProcess);//Close the process' handle
		}
	} while(Process32Next(hProcessSnap, &pEntry32));
 
	CloseHandle(hProcessSnap);
	return TRUE; //Succeed.
}


int main(int argc, char **argv)
{
	FILE *pyfile;
	int file_size;
	char* python_code  = 0;

	printf("+-------------------------------------------+\n");
	printf("| EVE Python Injector 4, by pxor128@gmail.com|\n");
	printf("| patched by wibiti, spheremonke y           |\n");
	printf("+--------------------------------------------+\n\n");

	if (argc != 2 || !strcmp(argv[1], "-h") || !strcmp(argv[1], "--help"))
	{
		printf ("usage: lolpy3 <file>\n");
		return(1);
	}

	pyfile = fopen (argv[1], "r");
	if (!pyfile)
	{
		printf("unable to read file: %s\n", argv[1]);
		return(1);
	}

	/* Read the python code into memory */
	fseek (pyfile, 0, SEEK_END);
	file_size = ftell (pyfile);
	fseek (pyfile, 0, SEEK_SET);
	python_code = (char*)calloc(1, file_size+1);
	fread ((void *)python_code, 1, file_size, pyfile);
	fclose (pyfile);

	InjectCode("exeFile.exe", python_code, file_size);

	return 0;
}
