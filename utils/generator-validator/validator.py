# Copyright (C) 2020 Marcel Meuter
import pyshark
import argparse
import yaml
import sys

COUNTER = {'smtp': 0, 'smb': 0, 'ipp': 0}


def print_source_destination(packet):
    print(
        f'[~] {packet.highest_layer}: {packet.sniff_time}: {packet.ip.src_host}:{packet.tcp.srcport} => {packet.ip.dst_host}:{packet.tcp.dstport}')


def parse_mail_content(smtp):
    fields = list(smtp._get_all_field_lines())
    fields = list(map(lambda field: field.strip()[:-4], fields))
    fields = list(filter(None, fields))
    return {'to': fields[0], 'from': fields[2], 'subject': fields[1], 'message': fields[15], 'date': fields[4]}


def parse_ipp_content(ipp):
    fields = list(ipp._get_all_field_lines())
    fields = list(map(lambda field: field.strip(), fields))
    fields = list(filter(None, fields))

    text = ipp.data.binary_value.decode('utf-8').strip()
    return {'uri': fields[21][12:-1], 'name': fields[12][33:-1], 'text': text}


def parse_mails(capture):
    cap = pyshark.FileCapture(capture, display_filter='smtp')

    for i, packet in enumerate(cap):
        if 'req_parameter' in packet.smtp.field_names and 'req_command' in packet.smtp.field_names:
            if packet.smtp.req_command == 'MAIL':
                print_source_destination(packet)

                print(f'\t\t{packet.smtp.req_parameter}')

            elif packet.smtp.req_command == 'RCPT':
                print_source_destination(packet)

                print(f'\t\t{packet.smtp.req_parameter}')
        elif 'req_command' in packet.smtp.field_names:
            if packet.smtp.req_command == 'DATA':
                print_source_destination(packet)

                packet = cap[i + 2]
                mail_content = parse_mail_content(packet.smtp)
                print(f'\t\t{mail_content["to"]} - {mail_content["from"]}- Subject: {mail_content["subject"]}')
                print(f'\t\tMessage: {mail_content["message"]}')
                print('----------------------------------------------')

                COUNTER['smtp'] += 1

    cap.close()


def parse_smb(capture):
    cap = pyshark.FileCapture(capture, display_filter='smb2')

    for i, packet in enumerate(cap):
        if int(str(packet.smb2.cmd)) == 0x5:
            if 'smb_access_write' in packet.smb2.field_names and int(str(packet.smb2.smb_access_write)):
                print_source_destination(packet)

                print(f'\t\tCreate File: {packet.smb2.get("Filename")} at {packet.smb2.tree}.')
                print('----------------------------------------------')

                COUNTER['smb'] += 1

    cap.close()


def parse_ipp(capture):
    cap = pyshark.FileCapture(capture, display_filter='ipp')

    for i, packet in enumerate(cap):
        if int(str(packet.ipp.request_id)) == 0x2:
            if 'data' in packet.ipp.field_names:
                print_source_destination(packet)

                print_job = parse_ipp_content(packet.ipp)
                print(f'\t\tPrint-Job: "{print_job["name"]}" to {print_job["uri"]}.')
                print(f'\t\t"{print_job["text"]}"')
                print('----------------------------------------------')

                COUNTER['ipp'] += 1

    cap.close()


def parse_config(config):
    try:
        with open(config, 'r') as f:
            config = yaml.safe_load(f)
    except (IOError, yaml.YAMLError) as error:
        print(f'[-] Could not find or parse config file {config}: {error}')
        sys.exit(1)

    requirements = {'smb': 0, 'ipp': 0, 'smtp': 0}

    for entry in list(config['hay'].values()) + list(config['needles'].values()):
        if entry['application'] == 'http':
            continue

        application_type = config['applications'][entry['application']]['type']
        if application_type == 'printer':
            requirements['ipp'] += entry['amount']
        elif application_type == 'smb':
            requirements['smb'] += entry['amount']
        elif application_type == 'mail':
            requirements['smtp'] += entry['amount']

    return requirements


def check_requirements(requirements, counter):
    requirements_failed = False
    for key, entry in requirements.items():
        if entry == counter[key]:
            print(f'[+] {key.upper()}: {counter[key]}/{entry} ({(counter[key] / entry) * 100}%) requests found.')
        else:
            print(f'[-] {key.upper()}: {counter[key]}/{entry} ({(counter[key] / entry) * 100}%) requests found.')
            requirements_failed = True

    if requirements_failed:
        sys.exit(1)


def main():
    # Parse command line arguments.
    parser = argparse.ArgumentParser(description='Haystack dump and config validator.')
    parser.add_argument('pcap', type=str, help='path to the .pcap file')
    parser.add_argument('config', type=str, help='path to the .yaml config file')

    args = parser.parse_args()

    requirements = parse_config(args.config)

    parse_mails(args.pcap)
    parse_smb(args.pcap)
    parse_ipp(args.pcap)

    print(f'[~] Found {COUNTER["smtp"]} SMTP send mail requests.')
    print(f'[~] Found {COUNTER["ipp"]} IPP print requests.')
    print(f'[~] Found {COUNTER["smb"]} SMB create file requests.')

    check_requirements(requirements, COUNTER)


if __name__ == '__main__':
    main()
