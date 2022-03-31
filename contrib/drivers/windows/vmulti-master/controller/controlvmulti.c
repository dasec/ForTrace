#include <windows.h>
#include <stdio.h>
#include <stdlib.h>
#include <tchar.h>

#include "vmulticlient.h"

typedef enum {
	DUMMY = 0,
	KB = 1,
	RMOUSE = 2,
	AMOUSE = 3,
	QUIT = 255,
} INPUT_TYPES;

// make sure that everything is aligned as it is
#pragma pack(1)

struct PipeContents {
	BYTE type;
	BYTE data[15];
};

struct RelativeMouseData {
	BYTE _dummy;
	BYTE button;
	BYTE x;
	BYTE y;
	BYTE wheel;
	BYTE _dummy2[11];
};

struct KeyboardData {
	BYTE _dummy;
	BYTE shiftkeys;
	BYTE keycodes[6];
	BYTE _dummy2[8];
};

#pragma pack()

//
// Implementation
//

INT __cdecl
main(
	int argc,
	PCHAR argv[]
	)
{
	struct PipeContents pipedata = { 0, 0 };
	pvmulti_client vmulti;
	HANDLE pipe = INVALID_HANDLE_VALUE;

	//
	// File device
	//

	vmulti = vmulti_alloc();

	if (vmulti == NULL)
	{
		return 2;
	}

	if (!vmulti_connect(vmulti))
	{
		vmulti_free(vmulti);
		return 3;
	}

	//
	// Create the named pipe
	//


	pipe = CreateNamedPipe(_T("\\\\.\\pipe\\vmultidev"), PIPE_ACCESS_INBOUND, PIPE_TYPE_BYTE | PIPE_WAIT, PIPE_UNLIMITED_INSTANCES, 16, 16, NMPWAIT_USE_DEFAULT_WAIT, NULL);

	if (pipe != INVALID_HANDLE_VALUE)
	{

		OutputDebugString(_T("Waiting for pipe client to connect...\n"));

		BOOL fConnected = ConnectNamedPipe(pipe, NULL) ?
			TRUE : (GetLastError() == ERROR_PIPE_CONNECTED);

		if (fConnected)
		{
			OutputDebugString(_T("Pipe client connected!\n"));
			while (1)
			{
				DWORD rbytes;
				while (1) //wait till sufficient amount of data is available
				{
					BOOL success = PeekNamedPipe(pipe, &pipedata, sizeof(pipedata), &rbytes, NULL, NULL);
					if (success && rbytes == 16)
						break;
					else
					{
						if (!success) // an error occured
						{
							DWORD err = GetLastError();
							HRESULT herr = HRESULT_FROM_WIN32(err);
							OutputDebugString(_T("Error while waiting for data!\n"));
							break;
						}
						Sleep(100);
					}
				}
				BOOL success = ReadFile(pipe, &pipedata, sizeof(pipedata), &rbytes, NULL);
				if (success)
				{
					switch (pipedata.type)
					{
					case KB:
					{
						struct KeyboardData *d = (struct KeyboardData*)&pipedata;
						vmulti_update_keyboard(vmulti, d->shiftkeys, d->keycodes);
						OutputDebugString(_T("Got kb_request\n"));
					}
					break;
					case RMOUSE:
					{
						struct RelativeMouseData *d = (struct RelativeMouseData*)&pipedata;
						vmulti_update_relative_mouse(vmulti, d->button, d->x, d->y, d->wheel);
						OutputDebugString(_T("Got mouse_request\n"));
					}
					case QUIT:
					default:
						break;
					}

				}
				else
				{
					DWORD err = GetLastError();
					HRESULT herr = HRESULT_FROM_WIN32(err);
					OutputDebugString(_T("Error occurred while reading from pipe!\n"));
					break;
				}
				ZeroMemory(&pipedata, sizeof(pipedata));
			}
		}
	}
	else
	{
		DWORD err = GetLastError();
		HRESULT herr = HRESULT_FROM_WIN32(err);
		OutputDebugString(_T("Pipe could not be created!\n"));

		vmulti_disconnect(vmulti);
		OutputDebugString(_T("Disconnected from driver!\n"));

		vmulti_free(vmulti);
		OutputDebugString(_T("Ressources freed!\n"));
		OutputDebugString(_T("Exiting!\n"));
		return -1;
	}

	CloseHandle(pipe);
	OutputDebugString(_T("Pipe handle closed!\n"));

	vmulti_disconnect(vmulti);
	OutputDebugString(_T("Disconnected from driver!\n"));

	vmulti_free(vmulti);
	OutputDebugString(_T("Ressources freed!\n"));

	return 0;
}
