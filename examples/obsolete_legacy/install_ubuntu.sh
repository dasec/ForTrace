sudo apt-get install spice-vdagent
sudo apt-get install subversion python-pip

# - Instant Messenger
sudo apt-get install pidgin

# - automate Firefox
pip install --user selenium

# - automate window actions
wget http://download.freedesktop.org/ldtp/3.x/3.5.x/ldtp-3.5.0.tar.gz -P ~/Downloads
pip install --user ~/Downloads/ldtp-3.5.0.tar.gz
# - ldtp dependecies
sudo apt-get install python-gnome2
sudo apt-get install python-twisted-web2
sudo apt-get install python-pyatspi
# - LDTP uses accessibility feature
gsettings set org.gnome.desktop.interface toolkit-accessibility true

# - malware-meta-framework requirements
sudo apt-get install python-enum34
sudo apt-get install python-protobuf
sudo apt-get install python-netifaces


cat > startAgent.sh <<EOL
cd \$(dirname \$0)
python guestAgent.py
EOL

chmod u+x startAgent.sh

path=$(realpath .)
cat > ~/.config/autostart/bash.desktop <<EOL
[Desktop Entry]
Type=Application
Exec=/usr/bin/gnome-terminal -x bash -c "${path}/startAgent.sh; bash"
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
Name=StartAgent
EOL