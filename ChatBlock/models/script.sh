# Change directory to the home directory
cd ~

sudo cp conf_file /etc/resolv.conf
# Remove existing Chatblock directory if it exists
rm -rf ChatBlock

# Clone the repository from GitHub
git clone https://github.com/terezann/ChatBlock.git

clear

cd ./ChatBlock/ChatBlock/models/ 

python3 node.py $1 $2 $3 $4
