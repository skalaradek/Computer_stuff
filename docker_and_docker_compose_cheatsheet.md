# 🐳 Docker + Docker Compose Cheat Sheet

## 🔧 Docker CLI Commands

### 📦 Image & Container Management
```
docker build -t myimage .           # Build image from Dockerfile
docker images                       # List all images
docker run -d -p 8080:80 myimage    # Run container in detached mode
docker ps                           # List running containers
docker stop <container>             # Stop container
docker start <container>            # Start container
docker rm <container>               # Remove container
docker rmi <image>                  # Remove image
```
### 🗂️ Volume & Network
```
docker volume ls                    # List volumes
docker volume rm <volume>           # Remove volume
docker network ls                   # List networks
docker network create <name>        # Create network
docker ps -q | xargs -n 1 docker inspect --format \
  '{{ .Name }} {{range .NetworkSettings.Networks}} {{.IPAddress}}{{end}}' \
  | sed 's#^/##'                    # Show hostnames with IP addresses
```
### 🔍 Inspect & Logs
```
docker logs <container>             # View logs
docker exec -it <container> bash    # Access container shell
docker inspect <container>          # Detailed info (JSON)
```
## 📘 Docker Compose Commands
### 🚀 Lifecycle
```
docker compose up -d                # Start all services in background
docker compose down                 # Stop and remove containers, networks, volumes
docker compose restart              # Restart all services
docker compose stop                 # Stop services
docker compose start                # Start services
```
### 🔍 Inspect & Logs
```
docker compose ps                   # List running services
docker compose logs                 # View logs for all services
docker compose logs <service>       # View logs for specific service
```
### 🛠️ Build & Config
```
docker compose build                # Build images from Dockerfile
docker compose config               # Validate and view full config
```
### 📈 Scaling
```
docker compose up --scale web=3     # Run 3 instances of 'web' service
```
### 🧠 Tips
Use .env files to manage environment variables cleanly.  
Use depends_on in docker-compose.yml to control service startup order.  
Use volumes: to persist data across container restarts.  
You can inspect volume contents using a temporary container:  
`docker run -it --rm -v mydata:/data alpine sh`  
This opens a shell in Alpine with your volume mounted at /data  
  
## 🛡️ What You Should Back Up
Named volumes (e.g., mydata)  
Bind-mounted directories (e.g., /home/radek/app/config)  
Database files or persistent storage paths  
Configuration files (e.g., .env, docker-compose.yml)  
  
### 📦 Backing Up Docker Volumes
1. Using tar with a temporary container
```
docker run --rm -v mydata:/data -v $(pwd):/backup alpine \
  tar czf /backup/mydata-backup.tar.gz -C /data .
```
This creates a compressed backup of the mydata volume in your current directory.  
  
2. Copying volume contents manually  
```
docker run --rm -v mydata:/data -v $(pwd):/backup alpine \
  cp -r /data /backup/
```
### 🗂️ Backing Up Bind Mounts
If you're using bind mounts (host directories), just back them up like any regular folder:
```
tar czf config-backup.tar.gz /home/docker/app/config
```
### 🧠 Tips
🔁 Automate backups with cron jobs or systemd timers.  
🧪 Test restores regularly to ensure your backups actually work.  
🗃️ Version your backups with timestamps: `backup-$(date +%F).tar.gz`  
☁️ Store offsite: Use cloud storage (e.g., S3, Dropbox, rsync to remote server).  
  
### 🧰 Restore Example
To restore a volume from a backup:  
```
docker run --rm -v mydata:/data -v $(pwd):/backup alpine \
  tar xzf /backup/mydata-backup.tar.gz -C /data
```
### 🐘 PostgreSQL Backup
#### 🔄 Backup
```
docker exec -t <postgres_container> \
  pg_dump -U <username> <database> > backup.sql
```
Example:  
```
docker exec -t my_postgres \
  pg_dump -U postgres mydb > mydb-backup.sql
```
This dumps the database mydb to a file on your host machine.

#### 🔁 Restore
```
cat mydb-backup.sql | docker exec -i <postgres_container> \
  psql -U <username> <database>
```
### 🐬 MySQL / MariaDB Backup
#### 🔄 Backup
```
docker exec <mysql_container> \
  mysqldump -u <username> -p<password> <database> > backup.sql
```
Example:  
```
docker exec my_mysql \
  mysqldump -u root -psecret mydb > mydb-backup.sql
```  
  
#### 🔁 Restore
```
cat mydb-backup.sql | docker exec -i <mysql_container> \
  mysql -u <username> -p<password> <database>
```
  
### 🧠 Docker Image Management Cheat Sheet
#### 🏗️ Create an Image from a Container
`docker commit <container_id> my-image:tag`  
Saves the current state of a container as a new image.  
  
#### 🏷️ Tag an Image
`docker tag my-image:tag username/my-image:tag`  
Prepares the image for pushing to a registry.  
  
#### 🚀 Push Image to Docker Hub
`docker push username/my-image:tag`  
Uploads the image to Docker Hub or another registry.  
  
#### 📥 Pull Image from Registry
`docker pull username/my-image:tag`  
Downloads the image from a registry.  
  
#### 📦 Save Image to Tar File
`docker save -o my-image.tar my-image:tag`  
Exports the image as a .tar archive for sharing offline.  
  
#### 📂 Load Image from Tar File
`docker load -i my-image.tar`  
Imports the image from a .tar archive.  
  
#### 🗑️ Remove Image
`docker rmi my-image:tag`  
Deletes the image from your local system.  
  
#### 📋 List Local Images
`docker images`  
Shows all images stored locally.  


