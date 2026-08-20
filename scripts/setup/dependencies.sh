# Sylvio Dos Reis, 2026
# Installs linux dependancies. Not to be run on Allianca Canada Computers

sudo apt update -y
sudo apt upgrade -y
sudo apt install -y gcc gfortran g++ git wget build-essential libpng-dev libcurl4-gnutls-dev m4 software-properties-common rename python3 python3-pip cmake zlib1g-dev pkg-config
sudo add-apt-repository -y universe
sudo apt -y install csh