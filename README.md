# Hermes
 Hermes's Thoughts

Decentralized P2P messaging built on the kademlia protocol.

## Setup

install git `sudo apt install git`
```shell
git clone https://github.com/Carroteh/Hermes
cd Hermes/
sudo chmod +x docker.sh #Add execute permissions to the docker.sh script
./docker.sh # Run the docker installing script
```
Once the git repository is downloaded and Docker is installed, build the docker image.

```aiignore
sudo docker build -t hermes .
```

Then to run the docker image:

```aiignore
sudo docker run -it --network  host hermes
```