# Generator Validator

## Overview

This tool can be used to check, whether a generated `.pcap` dump contains the actions (requests) previously defined in a `.yaml` config
file for the *fortrace* generator.

*Note: Python 3 is required for this tool to run.*

## Usage

> $ pip3 install -r requirements.txt  
> $ python3 validator.py <dump.pcap> <config.yaml>

## Output

```
$ python3 validator.py 1581506220.pcap example-haystack.yaml
[~] SMTP: 2020-02-12 15:42:58.988878: 192.168.103.7:49916 => 192.168.103.123:25
		FROM:<sk@fortrace.local> BODY=8BITMIME SIZE=32003
[~] SMTP: 2020-02-12 15:42:58.998717: 192.168.103.7:49916 => 192.168.103.123:25
		TO:<sk@fortrace.local>
[~] SMTP: 2020-02-12 15:42:59.007966: 192.168.103.7:49916 => 192.168.103.123:25
		To: sk@fortrace.local - From: Heinz fortrace <sk@fortrace.local>- Subject: Subject: a random mail
		Message: I'm sending you this mail because of X.
----------------------------------------------
[~] SMTP: 2020-02-12 15:44:25.175905: 192.168.103.7:49932 => 192.168.103.123:25
		FROM:<sk@fortrace.local> BODY=8BITMIME SIZE=14588
[~] SMTP: 2020-02-12 15:44:25.176454: 192.168.103.7:49932 => 192.168.103.123:25
		TO:<sk@fortrace.local>
[~] SMTP: 2020-02-12 15:44:25.177770: 192.168.103.7:49932 => 192.168.103.123:25
		To: sk@fortrace.local - From: Heinz fortrace <sk@fortrace.local>- Subject: Subject: Important Business Mail
		Message: Lorem ipsum dolor sit amet
----------------------------------------------
[~] SMTP: 2020-02-12 15:46:31.563740: 192.168.103.7:49947 => 192.168.103.123:25
		FROM:<sk@fortrace.local> BODY=8BITMIME SIZE=6673
[~] SMTP: 2020-02-12 15:46:31.571047: 192.168.103.7:49947 => 192.168.103.123:25
		TO:<sk@fortrace.local>
[~] SMTP: 2020-02-12 15:46:31.578928: 192.168.103.7:49947 => 192.168.103.123:25
		To: sk@fortrace.local - From: Heinz fortrace <sk@fortrace.local>- Subject: Subject: Private Matter
		Message: Stet clita kasd gubergren
----------------------------------------------
[~] SMTP: 2020-02-12 15:48:35.944971: 192.168.103.7:49972 => 192.168.103.123:25
		FROM:<sk@fortrace.local> BODY=8BITMIME SIZE=653264
[~] SMTP: 2020-02-12 15:48:35.951715: 192.168.103.7:49972 => 192.168.103.123:25
		TO:<sk@fortrace.local>
[~] SMTP: 2020-02-12 15:48:35.959064: 192.168.103.7:49972 => 192.168.103.123:25
		To: sk@fortrace.local - From: Heinz fortrace <sk@fortrace.local>- Subject: Subject: a suspicious mail
		Message: Sed diam nonumy eirmod tempor invidunt ut labore et dolore magna 
----------------------------------------------
[~] SMB2: 2020-02-12 15:45:18.578740: 192.168.103.7:49933 => 192.168.103.123:445
		Create File: top_secret.txt at \\192.168.103.123\sambashare.
----------------------------------------------
[~] SMB2: 2020-02-12 15:45:19.668490: 192.168.103.7:49933 => 192.168.103.123:445
		Create File: hda_master.pdf at \\192.168.103.123\sambashare.
----------------------------------------------
[~] IPP: 2020-02-12 15:41:56.108827: 192.168.103.7:49877 => 192.168.103.123:631
		Print-Job: "top_secret.txt - Editor" to http://192.168.103.123:631/ipp/print/name.
		"The secret ingredient of our burger recipe: fresh burger buns and 
       love."
----------------------------------------------
[~] IPP: 2020-02-12 15:45:20.451507: 192.168.103.7:49939 => 192.168.103.123:631
		Print-Job: "top_secret.txt - Editor" to http://192.168.103.123:631/ipp/print/name.
		"The secret ingredient of our burger recipe: fresh burger buns and 
       love."
----------------------------------------------
[~] Found 4 SMTP send mail requests.
[~] Found 2 IPP print requests.
[~] Found 2 SMB create file requests.
[+] SMB: 2/2 (100.0%) requests found.
[+] IPP: 2/2 (100.0%) requests found.
[+] SMTP: 4/4 (100.0%) requests found.
```