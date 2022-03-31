/**
 * @file pidgin_puppet.c
 * @author Sascha Kopp
 * @date 18 Jan 2015
 * @brief File containing the implementation of Pidgin Puppet.
 */
 
#include "pidgin_puppet.h"

//commands
const char * str_cmd_get_contact_list = "get_contact_list"; /**< Receive the contact list */
const char * str_cmd_send_im = "send_msg_to"; /**< Send a IM to buddy  */
const char * str_cmd_send_chat = "send_chat_msg_to"; /**< Send chat message, TODO: implement  */
const char * str_cmd_shutdown = "shutdown"; /**< Close Pidgin  */
const char * str_cmd_go_online = "go_online"; /**< Set account status to online */
const char * str_cmd_go_offline = "go_offline"; /**< Set account status to offline */

//status codes
const char * str_reply_ok = "ok"; /**< everything went well */
const char * str_reply_error = "error"; /**< something went wrong */
const char * str_reply_critical = "critical"; /**< something went terribly wrong */
const char * str_reply_event = "event"; /**< notification */

//status messages
const char * str_error_no_data = "no_data"; /**< empty list or nothing returned */
const char * str_error_no_match = "no_match"; /**< referenced name not found */
const char * str_error_generic_failure = "generic_error"; /**< generic failure */
const char * str_error_unknown = "unknown_command"; /**< command could not be parsed */
const char * str_error_unhandled = "unhandled"; /**< should not happen, switch-case statement went default */
const char * str_critical_no_account = "no_account"; /**< no account selected before operation */
const char * str_critical_bad_ptr = "bad_ptr"; /**< a non-optional argument was provided with a NULL-pointer */
const char * str_critical_out_of_mem = "out_of_mem"; /**< the process went out of memory */

//event message
const char * str_event_msg_im_in = "msg_im_in"; /**< an IM was received */
const char * str_event_file_in = "file_in"; /**< a file transfer was requested */
const char * str_event_file_in_complete = "file_in_complete"; /**< a file transfer was completed */

PurplePlugin *this_plugin = 0; /**< Pointer to this plugin instance */
PurpleAccount *account = NULL; /**< Pointer to the current selected account */

guint timerhandle; /**< Pointer to the main-loop handle */

volatile int run; /**< Boolean that shows if the worker thread should still run */
volatile int cbretval; /**< Return value of a main-loop operation */
volatile cb_message *dispatcher_data_im_send = NULL; /**< IM Data that is used by the main-loop, NULL if nothing should be processed */

struct sockaddr_in serveraddr; /**< Berkeley-Socket-API server address */
int sockethandle; /**< Socket handle */
int socketonline; /**< Boolean that shows if a working socket is available */

char recvbuf[SIZERECVBUF]; /**< Buffer for received data */
char sendbuf[SIZESENDBUF]; /**< Buffer for data that needs to be send */

gboolean non_default_server_address = FALSE; /**< Was dynamic memory allocation used for server address */
char * option_agent_server_address = SERVADDR; /**< The IP-Address of the agent server process */
int option_agent_server_port = SERVPORT; /**< The server port of the agent server process */
gboolean option_auto_accept_file = TRUE; /**< Defines if the plugin should accept or reject files */
gboolean option_auto_accept_authorization_request = TRUE; /**< Defines if the plugin should accept or reject new authorization requests */

#ifdef WIN32
HANDLE whandle; /**< WIN32: Handle for worker thread */
HANDLE sendmutex; /**< WIN32: Mutex that controls send buffer access */
#else
pthread_t whandle; /**< POSIX: Handle for worker thread */
pthread_mutex_t sendmutex = PTHREAD_MUTEX_INITIALIZER; /**< POSIX: Mutex that controls send buffer access */
#endif

#ifdef WIN32
//WIN32

void
lockSend(void)
{
	WaitForSingleObject(sendmutex, INFINITE);
}

void
unlockSend(void)
{
	ReleaseMutex(sendmutex);
}
#else
//Posix

void
lockSend(void)
{
	pthread_mutex_lock(&sendmutex);
}

void
unlockSend(void)
{
	pthread_mutex_unlock(&sendmutex);
}
#endif

void headertohost(char* buf)
{
	int i;
	amh *h = (amh*)buf;
	int *p;
	h->numofentries = ntohl(h->numofentries);
	h->length = ntohl(h->length);
	p = (int*)(buf + sizeof(amh));
	for(i=0; i < h->numofentries; i++)
	{
		*p = ntohl(*p);
		p++;
	}
}

void headertonet(char* buf)
{
	int i;
	amh *h = (amh*)buf;
	int *p;
	p = (int*)(buf + sizeof(amh));
	for(i=0; i < h->numofentries; i++)
	{
		*p = htonl(*p);
		p++;
	}
	h->numofentries = htonl(h->numofentries);
	h->length = htonl(h->length);
}

void printbufferedmessage(char* buf)
{
	char *arg;
	unsigned int offset;
	unsigned int i;
	amh *header = (amh*)buf;
	printf("length: %d\nentries:%d\n", header->length, header->numofentries);
	for(i=0; i < header->numofentries; i++)
	{
		arg = offsetentrytoptr(buf, i, &offset);
		printf("offset %d: \"%s\"\n", offset, arg);
	}
}

void sendpackstr(const char* str, unsigned int *argnum, unsigned int *bytecnt, amh *header)
{
	unsigned int length;
	unsigned int *offsetptr;
	char *argptr;
	length = strlen(str)+1; //NULL-Termination
	argptr = sendbuf + (*bytecnt);
	offsetptr = (unsigned int*)(sendbuf + sizeof(amh) + ((*argnum) * sizeof(offset_entry_t)));
	*offsetptr = *bytecnt;
	strcpy(argptr, str);
	(*bytecnt) += length;
	header->length = (*bytecnt);
	header->numofentries++;
	(*argnum)++;
}

void sendpackstatus(PIDGIN_PUPPET_RETVAL rval, unsigned int *argnum, unsigned int *bytecnt, amh *header)
{
	switch(rval)
	{
		case P_OK:
		{
			sendpackstr(str_reply_ok, argnum, bytecnt, header);
		}
		break;
		case P_GENERIC_FAIL:
		{
			sendpackstr(str_reply_error, argnum, bytecnt, header);
			sendpackstr(str_error_generic_failure, argnum, bytecnt, header);
		}
		break;
		case P_NO_ACCOUNT:
		{
			sendpackstr(str_reply_critical, argnum, bytecnt, header);
			sendpackstr(str_critical_no_account, argnum, bytecnt, header);
		}
		break;
		case P_NO_DATA:
		{
			sendpackstr(str_reply_error, argnum, bytecnt, header);
			sendpackstr(str_error_no_data, argnum, bytecnt, header);
		}
		break;
		case P_NO_MATCH:
		{
			sendpackstr(str_reply_error, argnum, bytecnt, header);
			sendpackstr(str_error_no_match, argnum, bytecnt, header);
		}
		break;
		case P_BAD_PTR:
		{
			sendpackstr(str_reply_critical, argnum, bytecnt, header);
			sendpackstr(str_critical_bad_ptr, argnum, bytecnt, header);
		}
		break;
		case P_OUT_OF_MEM:
		{
			sendpackstr(str_reply_critical, argnum, bytecnt, header);
			sendpackstr(str_critical_out_of_mem, argnum, bytecnt, header);
		}
		break;
		case P_UNKNOWN:
		{
			sendpackstr(str_reply_error, argnum, bytecnt, header);
			sendpackstr(str_error_unknown, argnum, bytecnt, header);
		}
		break;
		default:
		{
			//unhandled error code, should not happen
			sendpackstr(str_reply_error, argnum, bytecnt, header);
			sendpackstr(str_error_unhandled, argnum, bytecnt, header);
		}
	}
}

unsigned int sendgetinitialbytepos(unsigned int numofargs)
{
	unsigned int offset = 0;
	offset += sizeof(amh); //header
	offset += (numofargs*sizeof(offset_entry_t)); //each offset descriptor
	return offset;
}

char *
offsetentrytoptr(char* bufptr, unsigned int num, unsigned int *out_offset)
{
	int skip;
	char *ptr;
	if(bufptr == NULL)
		return NULL;
	if(out_offset != NULL)
		*out_offset = *(unsigned int*)(bufptr + sizeof(amh) + (sizeof(offset_entry_t)*num));
	ptr = bufptr;
	skip = sizeof(amh);
	ptr += skip;
	ptr += (sizeof(offset_entry_t)*num); //point to offset element
	ptr = (bufptr + *(int*)ptr); //add offset to receive buffer ptr
	return ptr;
}

void
demultiplexmessage(void)
{
	amh *send_header;
	char *cmd_ptr;
	//void *data;
	unsigned int argcnt = 0;
	unsigned int bpos;
	int srval;
	PIDGIN_PUPPET_RETVAL rval;
	cbretval = P_NO_VALUE;
	//PIDGIN_PUPPET_STATE state;
	printbufferedmessage(recvbuf); //debug info
	send_header = (amh*)sendbuf;
	//state = P_ACTION_DONE;
	cmd_ptr = offsetentrytoptr(recvbuf, 0, NULL);
	printf("cmd received: \"%s\"\n", cmd_ptr);
	lockSend(); //don't allow write to send buffer by callbacks
	memset(sendbuf, 0, SIZESENDBUF);
	//data = malloc(4096);
	if(!strcmp(cmd_ptr, str_cmd_get_contact_list))
	{
		GSList *base = NULL;
		GSList *list = NULL;
		unsigned int lsize = 0;
		rval = getContactList(&base, &lsize);
		list = base;
		if(rval == P_OK)
		{
			bpos = sendgetinitialbytepos(lsize + 2U); //amount of entries + 2 for command and state
			sendpackstr(cmd_ptr, &argcnt, &bpos, send_header);
			sendpackstatus(rval, &argcnt, &bpos, send_header);
			while(lsize > 0)
			{
				PurpleBuddy *b = (PurpleBuddy*)list->data;
				sendpackstr(b->name, &argcnt, &bpos, send_header);
				list = g_slist_next(list);
				lsize--;
			}
			g_slist_free(base); //needs to be freed
		}
		else
		{
			bpos = sendgetinitialbytepos(3U); //command, state, data
			sendpackstr(cmd_ptr, &argcnt, &bpos, send_header);
			sendpackstatus(rval, &argcnt, &bpos, send_header);
		}
		goto reply;
	}
	if(!strcmp(cmd_ptr, str_cmd_send_im))
	{
		char *buddyptr;
		char *msgptr;
		cb_message m;
		//unsigned int argcnt=0;
		buddyptr = offsetentrytoptr(recvbuf, 1U, NULL);
		msgptr = offsetentrytoptr(recvbuf, 2U, NULL);
		//rval = sendImToBuddyUnsafe(buddyptr, msgptr);
		m.sender = buddyptr;
		m.msg = msgptr;
		//purple_signal_emit(this_plugin, "buddy-send-im", &m);
		dispatcher_data_im_send = &m;
		while(cbretval==P_NO_VALUE);
		rval = cbretval;
		if(rval == P_OK)
		{
			bpos = sendgetinitialbytepos(2U); //2 for command and state
			sendpackstr(cmd_ptr, &argcnt, &bpos, send_header);
			sendpackstatus(rval, &argcnt, &bpos, send_header);
		}
		else
		{
			bpos = sendgetinitialbytepos(3U); //command, state, data
			sendpackstr(cmd_ptr, &argcnt, &bpos, send_header);
			sendpackstatus(rval, &argcnt, &bpos, send_header);
		}
		goto reply;
	}
	if(!strcmp(cmd_ptr, str_cmd_shutdown))
	{
		exit(0);
	}
	if(!strcmp(cmd_ptr, str_cmd_go_online))
	{
		rval = changeOnlineState(TRUE);
		if(rval == P_OK)
		{
			bpos = sendgetinitialbytepos(2U); //2 for command and state
			sendpackstr(cmd_ptr, &argcnt, &bpos, send_header);
			sendpackstatus(rval, &argcnt, &bpos, send_header);
		}
		else
		{
			bpos = sendgetinitialbytepos(3U); //command, state, data
			sendpackstr(cmd_ptr, &argcnt, &bpos, send_header);
			sendpackstatus(rval, &argcnt, &bpos, send_header);
		}
		goto reply;
	}
	if(!strcmp(cmd_ptr, str_cmd_go_offline))
	{
		rval = changeOnlineState(FALSE);
		if(rval == P_OK)
		{
			bpos = sendgetinitialbytepos(2U); //2 for command and state
			sendpackstr(cmd_ptr, &argcnt, &bpos, send_header);
			sendpackstatus(rval, &argcnt, &bpos, send_header);
		}
		else
		{
			bpos = sendgetinitialbytepos(3U); //command, state, data
			sendpackstr(cmd_ptr, &argcnt, &bpos, send_header);
			sendpackstatus(rval, &argcnt, &bpos, send_header);
		}
		goto reply;
	}
	//unhandled
	bpos = sendgetinitialbytepos(3U); //command, state, data
	sendpackstr(cmd_ptr, &argcnt, &bpos, send_header);
	sendpackstatus(P_UNKNOWN, &argcnt, &bpos, send_header);
	reply:
	//notifyAgent(state, data);
	//free(data);
	printbufferedmessage(sendbuf); //debug info
	headertonet(sendbuf); //swap byte-order to tcp/ip byte-order
	srval = send(sockethandle, sendbuf, ntohl(send_header->length), 0); //might be less than specified
	if(srval == 0)
	{
		//error
	}
	unlockSend(); //done unlock access to send buffer
	return;
}

void
listensocket(void)
{
	int received;
	amh *h;
	h = (amh*)recvbuf;
	received = 0; //used as offset
	memset(recvbuf, 0, SIZERECVBUF);
	do {
		int rv = recv(sockethandle, recvbuf+received, SIZERECVBUF-received, 0);
		if(rv <= 0)
		{
			printf("recv: Socket error (%d)!\n", rv);
			if(rv == 0 && run == 1)
			{
				//lost socket connection (reopen)
				lockSend();
				opensocket();
				unlockSend();
			}
			return; //socket closed or error occured
		}
		received += rv;
		printf("Got %u Bytes of %u\n", (unsigned int)rv, (unsigned int)ntohl(h->length));
	} while(received < ntohl(h->length));
	headertohost(recvbuf);
	printf("Demultiplexing\n");
	demultiplexmessage();
}

void
opensocket(void)
{
	int rc = -1;
	sockethandle = socket(AF_INET, SOCK_STREAM, 0);
	if(sockethandle < 0)
	{
		//error creating socket
		printf("Critical Error!\n");
	}
	memset(&serveraddr, 0x00, sizeof(struct sockaddr_in));
	serveraddr.sin_family = AF_INET;
	serveraddr.sin_port = htons(option_agent_server_port);
	serveraddr.sin_addr.s_addr = inet_addr(option_agent_server_address);
	while(rc < 0 && run > 0)
	{
		//printf("Trying to connect...\n");
		#ifdef WIN32
		Sleep(100U);
		#else
		sleep(1U);
		#endif
		printf("Trying to connect to agent...\n");
		rc = connect(sockethandle, (struct sockaddr *)&serveraddr, sizeof(serveraddr));
	}
	if(run == 0)
	{
		printf("Interrupted while connecting!\n");
		if(rc >= 0)
		{
			printf("But could still connect!\n");
		}
	}
	printf("Connected!\n");
	socketonline = 1;
}

void
destroysocket(void)
{
	close(sockethandle);
	sockethandle = -1;
	socketonline = 0;
}

#ifdef WIN32
//WIN32

void __cdecl
listenerWorker(LPVOID data)
{
	sendmutex = CreateMutex(NULL, FALSE, NULL);
	opensocket();
	printf("Listener started\n");
	while(run > 0)
	{
		listensocket();
	}
	destroysocket();
	printf("Listener stoped\n");
	CloseHandle(sendmutex);
	_endthread();
}

int
startAgentListener(void)
{
	HANDLE rc;
	run = 1;
	rc = (HANDLE)_beginthread(listenerWorker, 0, NULL);
	if((long)rc == -1L)
		return P_GENERIC_FAIL;
	whandle = rc;
	return P_OK;
}

int
stopAgentListener(void)
{
	shutdown(sockethandle, 0); //disable socket reads to unblock
	run = 0;
	WaitForSingleObject(whandle, INFINITE);
	return P_OK;
}

#else
//Posix

void*
listenerWorker(void* data)
{
	opensocket();
	printf("Listener started\n");
	while(run > 0)
	{
		listensocket();
	}
	destroysocket();
	printf("Listener stoped\n");
	pthread_exit(NULL);
}

int
startAgentListener(void)
{
	int rc;
	run = 1;
	rc = pthread_create(&whandle, NULL, listenerWorker, NULL);
	if(rc > 0)
		return P_GENERIC_FAIL;
	return P_OK;
}

int
stopAgentListener(void)
{
	shutdown(sockethandle, 0); //disable socket reads to unblock
	run = 0;
	pthread_join(whandle, NULL);
	return P_OK;
}
#endif

int
notifyAgent(PIDGIN_PUPPET_STATE state, void *data)
{
	int srval;
	unsigned int bpos = 0;
	unsigned int argcnt = 0;
	amh *send_header = (amh*)sendbuf;
	lockSend(); //don't allow write to send buffer event loop
	memset(sendbuf, 0, SIZESENDBUF);
	switch(state)
	{
		case P_MSG_IM_IN:
		{
			cb_message *m = (cb_message*)data;
			bpos = sendgetinitialbytepos(4U); //callback,event,sender,message
			sendpackstr(str_event_msg_im_in, &argcnt, &bpos, send_header);
			sendpackstr(str_reply_event, &argcnt, &bpos, send_header);
			sendpackstr(m->sender, &argcnt, &bpos, send_header);
			sendpackstr(m->msg, &argcnt, &bpos, send_header);
		}
		break;
		default:
			break;
	}
	printbufferedmessage(sendbuf); //debug info
	headertonet(sendbuf); //switch endianess of header to tcp/ip endianess
	srval = send(sockethandle, sendbuf, ntohl(send_header->length), 0); //might be less than specified
	if(srval == 0)
	{
		//error
	}
	unlockSend(); //done unlock access to send buffer
	return P_OK;
}

int
isBuddyOnline(const char *buddyname, int *retval)
{
	PurpleAccount *a;
	PurpleBuddy *b;
	gboolean bonline = FALSE;
	a = NULL;
	b = NULL;
	if(retval == NULL)
		return P_BAD_PTR;
	if(a == NULL)
		return P_NO_ACCOUNT;
	b = purple_find_buddy (a, buddyname);
	if (b == NULL)
		return P_NO_MATCH;
	bonline = PURPLE_BUDDY_IS_ONLINE(b);
	*retval = bonline;
	return P_OK;
}

int
getAllAccounts(GList **list, unsigned int *size)
{
	GList *l;
	unsigned int length;
	l = NULL;
	if(list==NULL)
		return P_BAD_PTR;
	*list = NULL;
	l = purple_accounts_get_all();
	if(l == NULL)
		return P_NO_DATA;
	length = g_list_length(l);
	if(size != NULL)
		*size = length;
	if(length == 0)
		return P_NO_DATA;
	/*
	while(l != NULL)
	{
		PurpleAccount *a = (PurpleAccount*)l->data;
		purple_notify_message(this_plugin, PURPLE_NOTIFY_MSG_INFO,
		a->protocol_id, a->username,
		NULL, NULL, NULL);
		l = g_list_next(l);
	}
	*/
	*list = l;
	return P_OK;
}

int
selectAccount(const char* accountname, const char* prot_id)
{
	PurpleAccount *a;
	const char *cprot_id;
	a = NULL;
	cprot_id = prot_id;
	if(cprot_id == NULL)
	{
		cprot_id = "prpl-jabber";
	}
	a = purple_accounts_find(accountname, cprot_id); //hardcode jabber/xmpp for now
	if(a == NULL)
	{
		purple_notify_message(this_plugin, PURPLE_NOTIFY_MSG_ERROR,
		"error", "acccount not found",
		NULL, NULL, NULL);
		return P_NO_MATCH; //not found
	}
	else
	{
		account = a;
	}
	return P_OK;
}

int
getContactList(GSList **list, unsigned int *size)
{
	PurpleAccount *a;
	GSList *lbase;
	//GSList *lcurrent;
	unsigned int length;
	lbase = NULL;
	//lcurrent = NULL;
	if(list == NULL)
		return P_BAD_PTR;
	a = account;
	if(a == NULL)
		return P_NO_ACCOUNT;
	lbase = purple_find_buddies(a, NULL); //account,name (NULL for all) needs to be freed
	if(lbase == NULL)
	{
		*list = NULL;
		return P_NO_DATA;
	}
	length = g_slist_length(lbase);
	if(length == 0)
	{
		g_slist_free (lbase);
		*list = NULL;
		return P_NO_DATA;
	}
	if(size != NULL)
		*size = length;
	//lcurrent = lbase;
	/*
	while(lcurrent != NULL)
	{
		PurpleBuddy *b = (PurpleBuddy*)lcurrent->data;
		purple_notify_message(this_plugin, PURPLE_NOTIFY_MSG_INFO,
		b->alias, b->name,
		NULL, NULL, NULL);
		//do something with buddy list item
		lcurrent = g_slist_next(lcurrent);
	}
	*/
	//g_slist_free (lbase);
	//lbase = NULL;
	*list = lbase;
	return P_OK;
}

int
sendMsgToBuddyUnsafe(const char* buddy, const char* msg)
{
	//purple_conv_chat_send (PurpleConvChat *chat, const char *message)
	return P_OK;
}

int
sendImToBuddyUnsafe(const char* buddy, const char* msg)
{
	PurpleAccount *a;
	PurpleConversation *conv;
	PurpleConvIm *im;
	PurpleConversationType t;
	a = account;
	if(a == NULL)
		return P_NO_ACCOUNT;
	if(buddy == NULL)
		return P_BAD_PTR;
	if(msg == NULL)
		return P_BAD_PTR;
	//PurpleConnection *pc = NULL;
	conv = NULL;
	im = NULL;
	t = PURPLE_CONV_TYPE_IM;
	conv = purple_find_conversation_with_account(t, buddy, a);
	if(conv == NULL)
	{
		conv = purple_conversation_new (t, a, buddy);
	}
	if(conv == NULL)
		return P_NO_MATCH; //not sure if it's possible to check that the buddy exists through this, maybe check at beginning
	//pc = purple_conversation_get_gc (conv);
	im = purple_conversation_get_im_data (conv);
	purple_conv_im_send (im, msg);
	//purple_conversation_destroy (conv); //check later if we leak memory
	
	return P_OK;
}

int
addBuddy(const char* buddyname)
{
	PurpleAccount *a;
	PurpleBuddy *buddy;
	PurpleContact *contact;
	PurpleGroup *group;
	PurpleBlistNode *node;
	//const char* message;
	a = account;
	//message = "Please add me!";
	buddy = NULL;
	contact = NULL;
	group = NULL;
	node = NULL;
	if(a == NULL)
		return P_NO_ACCOUNT;
	buddy = purple_buddy_new (a, buddyname, buddyname); //account,buddyname,alias
	purple_blist_add_buddy (buddy, contact, group, node);
	purple_account_add_buddy (a, buddy); //account,buddy,message?
	return P_OK;
}

int changeOnlineState(gboolean online)
{
	PurpleAccount *a;
	a = account;
	if(a == NULL)
		return P_NO_ACCOUNT;
	if(online == 0)
	{
		purple_account_set_status(a, "offline", TRUE, NULL);
	}
	else
	{
		purple_account_set_status(a, "available", TRUE, NULL);
	}
	return P_OK;
}

//Callbacks

void cbSendImToBuddy(void* cbmsg, void* data)
{
	cb_message m = *(cb_message*)cbmsg;
	printf("Entered Send Im signal handler\n");
	//gdk_threads_enter();
	cbretval = sendImToBuddyUnsafe(m.sender, m.msg);
	//gdk_threads_leave();
}

void
receivedImMsgCallback(PurpleAccount *account, char *sender, char *message,
                        PurpleConversation *conv, PurpleMessageFlags flags)
{
	//int retval;
	//purple_notify_message(this_plugin, PURPLE_NOTIFY_MSG_INFO,
    //        sender, message,
    //        NULL, NULL, NULL);
	//echo POC
	//retval = sendImToBuddyUnsafe(sender, message);
	//if(retval != P_OK)
	//	return;
	cb_message m;
	m.sender = sender;
	m.msg = message;
	notifyAgent(P_MSG_IM_IN, &m);
}

void
receivedChatMsgCallback(PurpleAccount *account, char *sender, char *message,
                              PurpleConversation *conv, PurpleMessageFlags flags)
{
	//printf("msg_in (%s)\n%s\n", sender, message);
	//purple_notify_message(this_plugin, PURPLE_NOTIFY_MSG_INFO,
    //        sender, message,
    //        NULL, NULL, NULL);
}

int
account_authorization_requested(PurpleAccount *account, const char *user)
{
	printf("Callback: User \"%s\" (%s) has sent a buddy request\n", user, purple_account_get_protocol_id(account));
	if(option_auto_accept_authorization_request == TRUE)
		return 1;  //authorize buddy request
	else
		return -1; //deny buddy request
}

void
signed_on(PurpleConnection *gc)
{
	PurpleAccount *acc = purple_connection_get_account(gc);
	printf("Callback: Account connected: \"%s\" (%s)\n", purple_account_get_username(acc), purple_account_get_protocol_id(acc));
}

void
buddy_signed_on(PurpleBuddy *buddy)
{
	printf("Callback: Buddy \"%s\" (%s) signed on\n", purple_buddy_get_name(buddy), purple_account_get_protocol_id(purple_buddy_get_account(buddy)));
}

void
buddy_signed_off(PurpleBuddy *buddy)
{
	printf("Callback: Buddy \"%s\" (%s) signed off\n", purple_buddy_get_name(buddy), purple_account_get_protocol_id(purple_buddy_get_account(buddy)));
}

void
file_recv_request(PurpleXfer *xfer, gpointer data)
{
	const char *filename;
	//PurpleAccount *account;
	const char *buddy;
	filename = purple_xfer_get_filename(xfer);
	//account = purple_xfer_get_account(xfer);
	buddy = purple_xfer_get_remote_user(xfer);
	printf("Callback: [%s] requested file transfer for: %s\n", buddy, filename);
	if(option_auto_accept_file == TRUE)
	{
		purple_xfer_request_accepted(xfer, filename);
	}
	else
	{
		xfer->status = PURPLE_XFER_STATUS_CANCEL_LOCAL;
	}
}

void
file_recv_accept(PurpleXfer *xfer, gpointer data)
{
	const char *filename;
	//PurpleAccount *account;
	const char *buddy;
	filename = purple_xfer_get_filename(xfer);
	//account = purple_xfer_get_account(xfer);
	buddy = purple_xfer_get_remote_user(xfer);
	printf("Callback: [%s] accepted file transfer for: %s\n", buddy, filename);
}

void
file_recv_complete(PurpleXfer *xfer, gpointer data)
{
	const char *filename;
	//PurpleAccount *account;
	const char *buddy;
	filename = purple_xfer_get_local_filename(xfer);
	//account = purple_xfer_get_account(xfer);
	buddy = purple_xfer_get_remote_user(xfer);
	printf("Callback: [%s] completed file transfer for: %s\n", buddy, filename);
}

//Actions

/* Sample code
 * This function is the callback for the plugin action we added. All we're
 * doing here is displaying a message. When the user selects the plugin
 * action, this function is called. */
static void
plugin_send_msg_poc(PurplePluginAction *action)
{
	//ignore above
	//POC send msg
	sendImToBuddyUnsafe("dummy2@archcore", "POC Message");
}

/* Sample Code
 * we tell libpurple in the PurplePluginInfo struct to call this function to
 * get a list of plugin actions to use for the plugin.  This function gives
 * libpurple that list of actions. */
static GList *
plugin_actions(PurplePlugin *plugin, gpointer context)
{
    /* some C89 (a.k.a. ANSI C) compilers will warn if any variable declaration
     * includes an initilization that calls a function.  To avoid that, we
     * generally initialize our variables first with constant values like NULL
     * or 0 and assign to them with function calls later */
    GList *list;
    PurplePluginAction *action;
    list = NULL;
    action = NULL;

    /* The action gets created by specifying a name to show in the UI and a
     * callback function to call. */
    action = purple_plugin_action_new("Send Message POC", plugin_send_msg_poc);

    /* libpurple requires a GList of plugin actions, even if there is only one
     * action in the list.  We append the action to a GList here. */
    list = g_list_append(list, action);

    /* Once the list is complete, we send it to libpurple. */
    return list;
}

/**
* Setups the signal handlers
**/
static void
setupSignals(void)
{
	purple_signal_connect(purple_conversations_get_handle(), "received-chat-msg", /* What to connect to */
        this_plugin, /* Object receiving the signal */
        PURPLE_CALLBACK(receivedChatMsgCallback), /* Callback function */
	NULL
        );
	purple_signal_connect(purple_conversations_get_handle(), "received-im-msg", /* What to connect to */
        this_plugin, /* Object receiving the signal */
        PURPLE_CALLBACK(receivedImMsgCallback), /* Callback function */
	NULL
        );
	purple_signal_connect(purple_accounts_get_handle(), "account-authorization-requested",
	this_plugin,
	PURPLE_CALLBACK(account_authorization_requested),
	NULL
	);
	purple_signal_connect(purple_connections_get_handle(), "signed-on",
	this_plugin,
	PURPLE_CALLBACK(signed_on),
	NULL
	);
	purple_signal_connect(purple_blist_get_handle(), "buddy-signed-on",
	this_plugin,
	PURPLE_CALLBACK(buddy_signed_on),
	NULL
	);
	purple_signal_connect(purple_blist_get_handle(), "buddy-signed-off",
	this_plugin,
	PURPLE_CALLBACK(buddy_signed_off),
	NULL
	);
	//
	purple_signal_connect(purple_xfers_get_handle(), "file-recv-request",
	this_plugin,
	PURPLE_CALLBACK(file_recv_request),
	NULL
	);
	purple_signal_connect(purple_xfers_get_handle(), "file-recv-accept",
	this_plugin,
	PURPLE_CALLBACK(file_recv_accept),
	NULL
	);
	purple_signal_connect(purple_xfers_get_handle(), "file-recv-complete",
	this_plugin,
	PURPLE_CALLBACK(file_recv_complete),
	NULL
	);
	//user defined
//	purple_signal_register( this_plugin, /* Instance */
//                "buddy-send-im",               /* Signal name */
//                purple_marshal_VOID__POINTER,/* Marshal function */
//                NULL,                        /* Callback return value type */
//                1,                           /* Number of callback arguments (not including void *data) */
//                purple_value_new(PURPLE_TYPE_SUBTYPE,PURPLE_TYPE_POINTER), /* Type of first callback argument */
//		purple_value_new(PURPLE_TYPE_SUBTYPE,PURPLE_TYPE_POINTER)
//                );
//	purple_signal_connect(this_plugin, "buddy-send-im",
//	this_plugin,
//	PURPLE_CALLBACK(cbsendImToBuddyUnsafe),
//	NULL
//	);
}

/**
* Event Loop for processing GUI-dependend data
**/
static gboolean
event_dispatcher_loop(gpointer data)
{
	if(dispatcher_data_im_send != NULL)
	{
		cb_message m = *dispatcher_data_im_send;
		//purple_signal_emit(this_plugin, "buddy-send-im", dispatcher_data_im_send); //obsolete
		dispatcher_data_im_send = NULL;
		cbretval = sendImToBuddyUnsafe(m.sender, m.msg);
	}
	return TRUE;
}

/**
* Will be called on plugin load
* Initializes the plugin including network, callbacks, etc.
**/
static gboolean
plugin_load(PurplePlugin *plugin) {
	GKeyFile *keyfile;
	GError *error;
	GList* aclist;
	PurpleAccount *a;
	int retval;
	gboolean kretval;
	this_plugin = plugin;
	error = NULL;
	socketonline = 0;
	
	keyfile = g_key_file_new();
	kretval = g_key_file_load_from_file(keyfile, "puppet.cfg", G_KEY_FILE_NONE, NULL);
	if(kretval == TRUE)
	{
		gchar* server_address;
		gint server_port;
		gboolean auto_file, auto_request;
		server_address = g_key_file_get_value(keyfile, "network", "server_address", &error);
		if(error != NULL)
		{
			g_error_free(error);
		}
		else
		{
			non_default_server_address = TRUE;
			option_agent_server_address = malloc(strlen(server_address)+1);
			memset(option_agent_server_address, 0, strlen(server_address)+1);
			strcpy(option_agent_server_address, server_address);
		}
		error = NULL;
		server_port = g_key_file_get_integer(keyfile, "network", "server_port", &error);
		if(error != NULL)
		{
			g_error_free(error);
		}
		else
		{
			option_agent_server_port = server_port;
		}
		error = NULL;
		auto_request = g_key_file_get_boolean(keyfile, "automation", "auto_accept_authorization_request", &error);
		if(error != NULL)
		{
			g_error_free(error);
		}
		else
		{
			option_auto_accept_authorization_request = auto_request;
		}
		error = NULL;
		auto_file = g_key_file_get_boolean(keyfile, "automation", "auto_accept_file", &error);
		if(error != NULL)
		{
			g_error_free(error);
		}
		else
		{
			option_auto_accept_file = auto_file;
		}
		error = NULL;
		
		g_key_file_free(keyfile);
	}
	else
	{
		printf("Error loading config: using defaults!\n");
	}
	
	printf("server address: %s\n", option_agent_server_address);
	printf("server port: %u\n", option_agent_server_port);
	printf("auto accepting authorization requests: %u\n", option_auto_accept_authorization_request);
	printf("auto accepting file transfers: %u\n", option_auto_accept_file);
	
	retval = getAllAccounts(&aclist, NULL);
	if(retval == P_OK)
	{
		a = (PurpleAccount*)(aclist->data);
	}
	else
	{
		//no data or error
		printf("Critical: no account data!\n");
		exit(-1);
		return TRUE;
	}
	retval = selectAccount(a->username, a->protocol_id);
	if(retval != P_OK)
	{
		printf("Critical: Could not select account!\n");
		exit(-2);
	}
	printf("Selected %s (%s)\n", a->username, a->protocol_id);
	//getContactList(NULL);
	setupSignals(); //setup the signal handlers
	startAgentListener(); //start network communication
	timerhandle = purple_timeout_add(100U, event_dispatcher_loop, NULL); //start the event loop
	return TRUE;
}

/**
* Will be called on plugin unload
* Uninitialized network and main loop
**/
static gboolean                       
plugin_unload(PurplePlugin *plugin)
{
	stopAgentListener();
	purple_timeout_remove(timerhandle);
	if(non_default_server_address == TRUE)
	{
		free(option_agent_server_address);
		non_default_server_address = FALSE;
		option_agent_server_address = SERVADDR;
	}
	return TRUE;
}

/**
* Contains basic informations to control plugin initialization
**/
static PurplePluginInfo info = {
	PURPLE_PLUGIN_MAGIC,
	PURPLE_MAJOR_VERSION,
	PURPLE_MINOR_VERSION,
	PURPLE_PLUGIN_STANDARD,
	NULL,
	0,
	NULL,
	PURPLE_PRIORITY_DEFAULT,

	"core-pidgin_puppet",
	"Pidgin Puppet",
	"0.2",

	"Remote Control Plugin",          
	"Remote Control Plugin",          
	"Sascha Kopp <sascha.kopp@stud.h-da.de>",                          
	"http://example.org",     
    
	plugin_load,                   
	plugin_unload,                          
	NULL,                          
                                   
	NULL,                          
	NULL,                          
	NULL,                        
	plugin_actions,                   
	NULL,                          
	NULL,                          
	NULL,                          
	NULL                           
};                               

/**
* Will be called on plugin initialization
**/
static void                        
init_plugin(PurplePlugin *plugin)
{
	
}

PURPLE_INIT_PLUGIN(pidgin_puppet, init_plugin, info)
