sudo apt-get -y  update; 
sudo apt-get -y upgrade;
sudo apt-get -y  autoclean;
sudo apt-get -y clean
sudo apt-get -y autoremove
sudo apt-get install gtkorphan -y
sudo apt-get install deborphan -y
sudo deborphan | xargs sudo apt-get -y remove --purge


