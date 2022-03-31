/* packet-mariposa.c
* It is based on the template from KenThompson:
* http://www.codeproject.com/KB/IP/custom_dissector.aspx
* got decrypt function from:
* http://defintel.com/docs/Mariposa_Analysis.pdf
* This program is free software; you can redistribute it and/or
* modify it under the terms of the GNU General Public License
* as published by the Free Software Foundation; either version 2
* of the License, or (at your option) any later version.
*
* This program is distributed in the hope that it will be useful,
* but WITHOUT ANY WARRANTY; without even the implied warranty of
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
* GNU General Public License for more details.
*
* You should have received a copy of the GNU General Public License
* along with this program; if not, write to the Free Software
* Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
*/

#ifdef HAVE_CONFIG_H
# include "config.h"
#endif

#include <stdio.h>
#include <glib.h>
#include <epan/packet.h>



#include <string.h>

#define PROTO_TAG_MARIPOSA	"MARIPOSA"

/* Wireshark ID of the mariposa protocol */
static int proto_mariposa = -1;

void decrypt(char *buf,int len);

/* These are the handles of our subdissectors */
static dissector_handle_t data_handle=NULL;

static dissector_handle_t mariposa_handle;
void dissect_mariposa(tvbuff_t *tvb, packet_info *pinfo, proto_tree *tree);

static int global_mariposa_port = 3333;

static const value_string packettypenames[] = {
	{ 0, "TEXT" },
	{ 1, "SOMETHING_ELSE" },
	{ 0, NULL }
};	

typedef unsigned char BYTE;
typedef unsigned int DWORD;
/* The following hf_* variables are used to hold the Wireshark IDs of
* our header fields; they are filled out when we call
* proto_register_field_array() in proto_register_mariposa()
*/
//static int hf_mariposa_pdu = -1;
/** Kts attempt at defining the protocol */
static gint hf_mariposa = -1;
static gint hf_mariposa_opcode = -1;
static gint hf_mariposa_seq = -1;
static gint hf_mariposa_original_data = -1;
static gint hf_mariposa_decrypt_data = -1;
static gint hf_mariposa_decrypt_data_cmd = -1;
static gint hf_mariposa_decrypt_data_cmd_content = -1;

/* These are the ids of the subtrees that we may be creating */
static gint ett_mariposa = -1;
static gint ett_mariposa_opcode = -1;
static gint ett_mariposa_seq = -1;
static gint ett_mariposa_original_data = -1;
static gint ett_mariposa_decrypt_data = -1;
static gint ett_mariposa_decrypt_data_cmd = -1;
static gint ett_mariposa_decrypt_data_cmd_content = -1;

void proto_reg_handoff_mariposa(void)
{
	static gboolean initialized=FALSE;

	if (!initialized) {
		data_handle = find_dissector("data");
		mariposa_handle = create_dissector_handle(dissect_mariposa, proto_mariposa);
		dissector_add("udp.port", global_mariposa_port, mariposa_handle);
		initialized = TRUE;
	}

}

void proto_register_mariposa (void)
{
	/* A header field is something you can search/filter on.
	* 
	* We create a structure to register our fields. It consists of an
	* array of hf_register_info structures, each of which are of the format
	* {&(field id), {name, abbrev, type, display, strings, bitmask, blurb, HFILL}}.
	*/
	static hf_register_info hf[] = 
	{
		{&hf_mariposa,
		    {"Data", 
		     "mariposa.data", 
		     FT_NONE, 
		     BASE_NONE, 
		     NULL, 
		     0x0,
		     "MARIPOSA PDU", 
		     HFILL 
		     }
		},
		{ &hf_mariposa_opcode,
		    { "Opcode", 
		        "mariposa.opcode", 
		        FT_UINT8, 
		        BASE_HEX, 
		        NULL, 
		        0x0,
		        "Opcode Number", 
		        HFILL 
		    }
		},
		{ &hf_mariposa_seq,
		    { "Seq", 
		        "mariposa.seq", 
		        FT_UINT16, 
		        BASE_HEX, 
		        NULL, 
		        0x0,
		        "Package seq number", 
		        HFILL 
		    }
		},
		{ &hf_mariposa_original_data,
		    { "Original Data", 
		        "mariposa.original_data", 
		        FT_BYTES, 
		        BASE_NONE, 
		        NULL, 
		        0x0,
		        "Original Data", 
		        HFILL 
		     }
		 },
		{ &hf_mariposa_decrypt_data,
		    { "Decrypted Data", 
		        "mariposa.decrypt_data", 
		        FT_BYTES, 
		        BASE_NONE, 
		        NULL, 
		        0x0,
		        "Decrypted Data", 
		        HFILL 
		     }
		 } ,
    	 { &hf_mariposa_decrypt_data_cmd,
    	    { "BOT cmd", 
    	        "mariposa.decrypt_data.cmd", 
    	        FT_UINT8, 
    	        BASE_HEX, 
    	        NULL, 
    	        0x0,
    	        "BOT cmd", 
    	        HFILL 
    	     }
    	 },
    	 { &hf_mariposa_decrypt_data_cmd_content,
    	    { "BOT cmd Content", 
    	        "mariposa.decrypt_data.cmd", 
    	        FT_BYTES, 
    	        BASE_NONE, 
    	        NULL, 
    	        0x0,
    	        "BOT cmd", 
    	        HFILL 
    	     }
    	 } 
	};
	static gint *ett[] = {
		&ett_mariposa,
		&ett_mariposa_opcode,
		&ett_mariposa_seq,
		&ett_mariposa_original_data,
		&ett_mariposa_decrypt_data
	};
	//if (proto_mariposa == -1) { /* execute protocol initialization only once */
	proto_mariposa = proto_register_protocol ("MARIPOSA Protocol", "MARIPOSA", "mariposa");

	proto_register_field_array (proto_mariposa, hf, array_length (hf));
	proto_register_subtree_array (ett, array_length (ett));
	register_dissector("mariposa", dissect_mariposa, proto_mariposa);
	//}
}
	

static void
dissect_mariposa(tvbuff_t *tvb, packet_info *pinfo, proto_tree *tree)
{

	proto_item *mariposa_item = NULL;
	proto_item *mariposa_decrypt_item = NULL;
	proto_tree *mariposa_tree = NULL;
	guint8 opcode = 0;
	guint16 seq=0;
    gint all_data_len,decrypt_data_len;
    guchar * Newbuf;
    tvbuff_t *next_tvb;
    
	if (check_col(pinfo->cinfo, COL_PROTOCOL))
		col_set_str(pinfo->cinfo, COL_PROTOCOL, PROTO_TAG_MARIPOSA);
	/* Clear out stuff in the info column */
	if(check_col(pinfo->cinfo,COL_INFO)){
		col_clear(pinfo->cinfo,COL_INFO);
	}

	// This is not a good way of dissecting packets.  The tvb length should
	// be sanity checked so we aren't going past the actual size of the buffer.
	opcode = tvb_get_guint8( tvb, 0); // Get the type byte

	if (check_col(pinfo->cinfo, COL_INFO)) {
		col_add_fstr(pinfo->cinfo, COL_INFO, "%d > %d Info opcode:[0x%x]",
		pinfo->srcport, pinfo->destport, opcode);
	}

	if (tree) { /* we are being asked for details */
		guint32 offset = 0;
		guint32 length = 0;
        
		mariposa_item = proto_tree_add_item(tree, proto_mariposa, tvb, 0, -1, FALSE);
		mariposa_tree = proto_item_add_subtree(mariposa_item, ett_mariposa);
		mariposa_decrypt_item = proto_item_add_subtree(mariposa_tree, ett_mariposa_decrypt_data);

        all_data_len = tvb_length_remaining(tvb, 0);
        if(all_data_len < 4) return;
        
        Newbuf = (guchar*) g_malloc(all_data_len);
        tvb_memcpy(tvb,Newbuf, 0, all_data_len);
        decrypt(Newbuf, all_data_len);
        decrypt_data_len = all_data_len - 3;
        next_tvb = tvb_new_child_real_data(tvb, Newbuf+3, decrypt_data_len, decrypt_data_len);
		add_new_data_source(pinfo, next_tvb, "Decrypted Data");
    
        proto_tree_add_uint(mariposa_tree, hf_mariposa_opcode, tvb, offset, 1, opcode);
        offset++;
        seq =  tvb_get_ntohs(tvb,offset);
        proto_tree_add_uint(mariposa_tree, hf_mariposa_seq, tvb, offset, 2, seq);
        offset+=2;
        proto_tree_add_bytes(mariposa_tree, hf_mariposa_original_data, tvb, offset, decrypt_data_len, tvb_get_ptr(tvb, offset, -1));
        
        proto_tree_add_bytes(mariposa_tree, hf_mariposa_decrypt_data, next_tvb, 0, decrypt_data_len, tvb_get_ptr(next_tvb, 0, -1));
        
        opcode = tvb_get_guint8(next_tvb, 0);
        
        proto_tree_add_uint(mariposa_decrypt_item, hf_mariposa_decrypt_data_cmd, next_tvb, 0, 1, opcode);
        proto_tree_add_bytes(mariposa_decrypt_item, hf_mariposa_decrypt_data_cmd_content, next_tvb, 1, decrypt_data_len - 1, tvb_get_ptr(next_tvb, 1, -1));
        
	}
}	


void decrypt(char *buf,int len)
{
    BYTE not,alt, low8bit;
    BYTE xor[2];
    int cnt1;
    
    low8bit = (len - 3) & 0xff; 
    not = ~low8bit;
    xor[0] = not ^ buf[1];
    xor[1] = not ^ buf[2];
    alt = 0;
    for(cnt1=3;cnt1 < len; cnt1++)
    {
        buf[cnt1] = buf[cnt1] ^ xor[alt];
        alt ^= 1;
    }
}