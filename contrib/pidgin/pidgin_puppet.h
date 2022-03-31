/**
 * @file pidgin_puppet.h
 * @author Sascha Kopp
 * @date 18 Jan 2015
 * @brief File containing header definitions of Pidgin Puppet.
 */

 /** @mainpage Documentation of Pidgin Puppet
 *
 * @section intro_sec Introduction
 *
 * This is the documentation of Pidgin Puppet.<br>
 * This Plugin provides an interface for the fortrace agent application to remotely control libpurple based messengers.<br>
 * Pidgin Puppet is implemented as a C-plugin for libpurple and can also be used in other libpurple based messengers.<br>
 * The API follows COM-style coding guidelines.<br>
 * You can find the fortrace project master page at: <a href="http://fortrace.fbi.h-da.de">http://fortrace.fbi.h-da.de</a>
 *
 * @section install_sec Installation
 *
 * @subsection step1 Step 1: Locate the plugin directory
 *
 * On Windows the location can be found on: "%APPDATA%\.purple\plugins"<br>
 * On Linux the location can be found on: "~/.purple/plugins"
 *
 * @subsection step2 Step 2: Copy the plugin into the directory
 *
 * @subsection step3 Step 3: Enable the plugin
 *
 * This step refers to a Pidgin installation.<br>
 * Note: Plugin activation may differ on different libpurple clients.<br>
 * Start Pidgin and open the "Plugins" entry under "Extras".<br>
 * Enable Pidgin Puppet from the list of plugins.<br>
 * Note: If no account exists Pidgin will terminate.
 *
 * @section communication_sec Communication
 *
 * Here is a brief overview of the protocol used to communicate with a protocol application:<br>
 *
 * @subsection com1 Format
 *
 * A packet can be broken down into length, number of offsets, Offset Table, String Table.
 *
 * @subsection com2 Header
 *
 * The header consists of the 32bit length filed and the 32bit offset number field.<br>
 * It is encoded in network byte-order.
 *
 * @subsection com3 Offset Table
 *
 * The Offset Table consists of a variable amount of 32bit offsets in network byte-order.<br>
 * The length is specified in the header.<br>
 * Offsets start from the beginning of the packet.
 *
 * @subsection com4 String Table
 *
 * The String table consists of a variable amount of NULL-terminated strings.<br>
 * The begin of each string is specified in the Offset Table.<br>
 * A string chain consists of the following elements:<br>
 * command:<br>
 * command + param1 + param2 + ... + paramn<br>
 * reply:<br>
 * command/event + status code + value1 + value2 + ... + valuen
 *
 * @section compilation_sec Compilation
 *
 * The source code uses the compiler infrastructure provided by the Pidgin source code.<br>
 * Copy the source code to the pidgin/plugins directory and refer to the official Pidgin documentation located here:<br>
 * <a href="https://developer.pidgin.im/wiki/CHowTo/BasicPluginHowto">BasicPluginHowto</a><br>
 * <a href="https://developer.pidgin.im/wiki/BuildingWinPidgin">BuildingWinPidgin</a>
 *
 */
 
 /**
 * This is a libpurple plugin
 **/
#define PURPLE_PLUGINS

#include <glib.h>
#ifndef G_GNUC_NULL_TERMINATED
#  if __GNUC__ >= 4
/**
* Generic bug fix provided by pidgin
**/
#    define G_GNUC_NULL_TERMINATED __attribute__((__sentinel__))
#  else
/**
* Generic bug fix provided by pidgin
**/
#    define G_GNUC_NULL_TERMINATED
#  endif /* __GNUC__ >= 4 */
#endif /* G_GNUC_NULL_TERMINATED */

#include <memory.h>

#ifdef WIN32
#include <windows.h>
#include <process.h>
#include <winsock2.h>
#include <ws2tcpip.h>
/**
* WIN32 doesn't define close use closesocket for that
**/
#define close closesocket
#else
#include <pthread.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <netdb.h>
#include <unistd.h>
#include <errno.h>
#endif

#include "eventloop.h"
#include "conversation.h"
#include "blist.h"
#include "cmds.h"
#include "notify.h"
#include "plugin.h"
#include "version.h"
#include "debug.h"
#include "ft.h"

#define SERVADDR "127.0.0.1" /**< IP address of agent */
#define SERVPORT 11001 /**< Port used for agent communication */
#define SIZERECVBUF 4096 /**< Buffer size of receive buffer */
#define SIZESENDBUF 4096 /**< Buffer size of send buffer */

/**
* @enum PIDGIN_PUPPET_RETVAL
* Enum that contains status codes for internal use
**/
typedef enum {
	P_OK = 0, /**< Success */
	P_GENERIC_FAIL = 1, /**< Generic failure */
	P_NO_ACCOUNT = 2, /**< No account selected */
	P_NO_DATA = 3, /**< No data or empty list was returned */
	P_NO_MATCH = 4, /**< Referenced object was not found */
	P_BAD_PTR = 5, /**< A Null-pointer was provided, but argument was not optional */
	P_OUT_OF_MEM = 6, /**< Could not allocate memory */
	P_UNKNOWN = 7, /**< Unknown command*/
	P_NO_VALUE = -1, /**< Value is not available, used for inter-thread communication */
} PIDGIN_PUPPET_RETVAL;

/**
* @enum PIDGIN_PUPPET_STATE
* Enum that contains status messages for internal use
**/
typedef enum {
	P_PLUGIN_UP, /**< Plugin went up */
	P_PLUGIN_DOWN, /**< Plugin went down */
	P_ACTION_DONE, /**< Action was completed */
	P_MSG_IM_IN, /**< IM received */
	P_MSG_CHAT_IN, /**< Chat message received */
	P_FILE_IN, /**< File received */
	P_CONTACT_NEW, /**< Authorization request received */
	P_SERVER_DOWN, /**< Server went down */
	P_SIGN_ON, /**< Self signed on */
	P_BUDDY_SIGN_ON, /**< Buddy went online */
	P_BUDDY_SIGN_OFF, /**< Buddy went offline */
} PIDGIN_PUPPET_STATE;

/**
* 32bit length field of header
* @typedef hlength_t
**/
typedef unsigned int hlength_t;
/**
* 32bit offset number field of header
* @typedef hnum_t
**/
typedef unsigned int hnum_t;
/**
* 32bit offset field of header
* @typedef offset_entry_t
**/
typedef unsigned int offset_entry_t;

/**
* Header used for agent communication
* @struct agentmessageheader
**/
typedef struct {
	hlength_t length; /**< Length of packet in bytes */
	hnum_t numofentries; /**< Number of offsets in packet */
} agentmessageheader; /**< Name for agent message headers */

/**
* Name shortener for a message header
* @typedef amh
**/
typedef agentmessageheader amh;

/**
* Struct contains pointers to a sender and a message string<br>
* Originally used for callbacks
* @struct cb_message
**/
typedef struct {
	char *sender; /**< Pointer to sender string */
	char *msg; /**< Pointer to message string */
} cb_message; /**< Name for message data */

//helpers
/** @{ */
/** @name helpers */
/**
* Transform header to host byte-order
* @param[in] buf Pointer to header
**/
void headertohost(char* buf);
/**
* Transform header to network byte-order
* @param[in] buf Pointer to header
**/
void headertonet(char* buf);
/**
* Prints a packet
* Packets needs to be in host byte-order
* @param[in] buf Pointer to send or receive buffer
**/
void printbufferedmessage(char* buf);
/**
* Returns pointer to a receive buffer entry
* @param[in] bufptr Pointer to a header
* @param[in] num Entry no., starts at 0
* @param[out] out_offset Pointer to the offset entry, optional
* @return Pointer to the string data requested
**/
char * offsetentrytoptr(char* bufptr, unsigned int num, unsigned int *out_offset);
/**
* Add a string to packet, will auto-increment message length, argument number and byte position
* @param[in] str String pointer which contents will be added to the packet
* @param[in,out] argnum Pointer to the current argument number of added string, auto-incremented
* @param[in,out] bytecnt Pointer to the curent byte count, auto-incremented
* @param[in] header Pointer to a send header
**/
void sendpackstr(const char* str, unsigned int *argnum, unsigned int *bytecnt, amh *header);
/**
* Returns the offset to the first byte after header
* @param[in] numofargs Number of arguments to reserve space for
* @return Number of reserved bytes including header
**/
unsigned int sendgetinitialbytepos(unsigned int numofargs);
/**
* Lock send buffer access
**/
void lockSend(void);
/**
* Unlock send buffer access
**/
void unlockSend(void);
/**
* Packs return status to header
* @param rval The status to be added
* @param argnum Pointer to argument number
* @param bytecnt Pointer to current byte count
* @param header Pointer to the header
* @warning On @ref P_OK only one slot is used
**/
void sendpackstatus(PIDGIN_PUPPET_RETVAL rval, unsigned int *argnum, unsigned int *bytecnt, amh *header);
/** @} */
//signals
/** @{ */
/** @name signals */
/**
* obsolete callback to send a message
* @param[in] cbmsg Pointer to a cb_message struct
* @param[in] data Internal Pointer to additional data, unused
**/
void cbSendImToBuddy(void* cbmsg, void* data);
/** @} */
//network
/** @{ */
/** @name network */
/**
* Deconstructs a message and calls the appropriate command<br>
* Notify agent of success of the received and processed command
**/
void demultiplexmessage(void);
/**
* Checks if message arrives and stores it to buffer
**/
void listensocket(void);
/**
* Establish connection to agent
**/
void opensocket(void);
/**
* Close the socket
**/
void destroysocket(void);
#ifdef WIN32
/**
* Thread to handle network communication with agent
* @param[in] data Internal pointer to additional data, unused
**/
void __cdecl listenerWorker(LPVOID data);
#else
/**
* Thread to handle network communication with agent
* @param[in] data Internal pointer to additional data, unused
* @return Internal pointer result data, no value return
**/
void* listenerWorker(void* data);
#endif
/**
* Starts the agent listener<br>
* May return: @ref P_OK, @ref P_GENERIC_FAIL
* @return Status code resulting from executed operation
**/
int startAgentListener(void);
/**
* Stops the agent listener<br>
* May return: @ref P_OK
* @return Status code resulting from executed operation
**/
int stopAgentListener(void);
/** @} */
//commands
/** @{ */
/** @name commands */
/**
* Notify Agent for state change<br>
* May return: @ref P_OK
* @param[in] state Internal state code to notify for
* @param[in] data Pointer to data used in switch-case statement
* @return Status code resulting from executed operation
**/
int notifyAgent(PIDGIN_PUPPET_STATE state, void *data);
/**
* Check if buddy is online, untested<br>
* May return: @ref P_OK, @ref P_BAD_PTR, @ref P_NO_ACCOUNT, @ref P_NO_MATCH
* @param[in] buddyname Name of buddy to check for state
* @param[in] retval Pointer to return value to write to (gboolean)
* @return Status code resulting from executed operation
**/
int isBuddyOnline(const char *buddyname, int *retval);
/**
* Gets a list of all registered accounts<br>
* May return: @ref P_OK, @ref P_BAD_PTR, @ref P_NO_DATA
* @param[out] list Pointer to list reference, will be initialized by function
* @param[in] size Pointer to size of list, that will be returned
* @return Status code resulting from executed operation
* @bug This function is untested.
**/
int getAllAccounts(GList** list, unsigned int *size);
/**
* Switch to a specific account for further actions ("user@server/resource"), if prot_id == NULL use xmpp<br>
* Needs to be called before every thing else<br>
* If not, most operations will fail with @ref P_NO_ACCOUNT<br>
* May return: @ref P_OK, @ref P_NO_MATCH
* @param[in] accountname Pointer to account name string ("user@server/resource" for xmpp)
* @param[in] prot_id Pointer to libpurple protocol id string, optional, xmpp is default
* @return Status code resulting from executed operation
**/
int selectAccount(const char* accountname, const char* prot_id);
/**
* Returns all buddies in selected account, returned list needs to be freed with g_slist_free if operation succeeded<br>
* May return: @ref P_OK, @ref P_BAD_PTR, @ref P_NO_DATA
* @param[out] list Pointer to list reference, will be initialized by function, needs to be freed with g_slist_free if operation succeeded
* @param[in] size Pointer to size of list, that will be returned
* @return Status code resulting from executed operation
**/
int getContactList(GSList **list, unsigned int *size);
/**
* Send Message to buddy using Chat Messages<br>
* May return: @ref P_OK
* @param[in] buddy Pointer to buddy name
* @param[in] msg Pointer to message that will be send to buddy
* @return Status code resulting from executed operation
* @warning Should only be called from main thread
* @bug This function is not implemented.
**/
int sendMsgToBuddyUnsafe(const char* buddy, const char* msg);
/**
* Send Message to buddy using Instant Messaging<br>
* May return: @ref P_OK, @ref P_BAD_PTR, @ref P_NO_MATCH
* @param[in] buddy Pointer to buddy name
* @param[in] msg Pointer to message that will be send to buddy
* @return Status code resulting from executed operation
* @warning Should only be called from main thread
**/
int sendImToBuddyUnsafe(const char* buddy, const char* msg);
/**
* Add a buddy to current account and send authorization request<br>
* May return: @ref P_OK, @ref P_NO_ACCOUNT
* @param[in] buddyname Pointer to buddy name that will be added
* @return Status code resulting from executed operation
**/
int addBuddy(const char* buddyname);
/**
* Sets state to on-/offline<br>
* May return: @ref P_OK, @ref P_NO_ACCOUNT
* @param online True for inline, False for Offline
* @return Status code resulting from executed operation
**/
int changeOnlineState(gboolean online);
/** @} */
//callbacks
/** @{ */
/** @name callbacks */
/** 
* Callback for Instant Messages
* @param[in] account Pointer to account, that received the IM
* @param[in] sender Pointer to buddy name, that received the IM
* @param[in] message Pointer to the actual message
* @param[in] conv Pointer to the conversation object
* @param[in] flags Flags of the received message
**/
void receivedImMsgCallback(PurpleAccount *account, char *sender, char *message,
                        PurpleConversation *conv, PurpleMessageFlags flags);
/** 
* Callback for Chat Messages
* @param[in] account Pointer to account, that received the chat message
* @param[in] sender Pointer to buddy name, that received the chat message
* @param[in] message Pointer to the actual message
* @param[in] conv Pointer to the conversation object
* @param[in] flags Flags of the received message
**/
void receivedChatMsgCallback(PurpleAccount *account, char *sender, char *message,
                              PurpleConversation *conv, PurpleMessageFlags flags);
/**
* Callback for Authorization Requests
* @param[in] account Pointer to account, that received the authorization request
* @param[in] user Pointer to buddy name, that send the authorization request
* @return 1 for accept, -1 for deny (default: accept)
**/
int account_authorization_requested(PurpleAccount *account, const char *user);
/**
* Callback for self server sign on
* @param[in] gc Pointer to a PurpleConnection object
**/
void signed_on(PurpleConnection *gc);
/**
* Callback for buddy sign on
* @param[in] buddy Pointer to the name of a signed on buddy
**/
void buddy_signed_on(PurpleBuddy *buddy);
/**
* Callback for buddy sign off
* @param[in] buddy Pointer to the name of a signed off buddy
**/
void buddy_signed_off(PurpleBuddy *buddy);
/**
* Callback for incoming file
* @param[in] xfer Pointer to a PurpleXfer object
* @param[in] data Additional data
**/
void file_recv_request(PurpleXfer *xfer, gpointer data);
/**
* Callback for incoming file accepted
* @param[in] xfer Pointer to a PurpleXfer object
* @param[in] data Additional data
**/
void file_recv_accept(PurpleXfer *xfer, gpointer data);
/**
* Callback for incoming file transfer completed
* @param[in] xfer Pointer to a PurpleXfer object
* @param[in] data Additional data
**/
void file_recv_complete(PurpleXfer *xfer, gpointer data);
/** @} */
