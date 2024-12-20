# main.tf
provider "aws" {
  region = "ap-southeast-1" # Found Singapore most suitable for lower latency
}

# VPC
resource "aws_vpc" "vaccine_vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true
  
  tags = {
    Name = "vaccine-system-vpc"
  }
}

# Internet Gateway
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.vaccine_vpc.id

  tags = {
    Name = "vaccine-system-igw"
  }
}

# Route Table for Public Subnet
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.vaccine_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = {
    Name = "public-rt"
  }
}

# Route Table Association for Public Subnet
resource "aws_route_table_association" "public" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}

# Public Subnet
resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.vaccine_vpc.id
  cidr_block              = "10.0.1.0/24"
  map_public_ip_on_launch = true
  
  tags = {
    Name = "public-subnet"
  }
}

# Private Subnet
resource "aws_subnet" "private" {
  vpc_id     = aws_vpc.vaccine_vpc.id
  cidr_block = "10.0.2.0/24"
  
  tags = {
    Name = "private-subnet"
  }
}

# Security Groups
resource "aws_security_group" "frontend" {
  name        = "cloud-vaccine-frontend-sg"
  description = "Security group for frontend of cloud vaccine webapp"
  vpc_id      = aws_vpc.vaccine_vpc.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "backend" {
  name        = "cloud-vaccine-backend-sg"
  description = "Security group for backend of cloud vaccine webapp"
  vpc_id      = aws_vpc.vaccine_vpc.id

  ingress {
    from_port       = 8000
    to_port         = 8000
    protocol        = "tcp"
    security_groups = [aws_security_group.frontend.id]
  }

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Security Group for MariaDB
resource "aws_security_group" "mariadb" {
  name        = "mariadb-sg"
  description = "Security group for MariaDB"
  vpc_id      = aws_vpc.vaccine_vpc.id

  ingress {
    from_port       = 3306
    to_port         = 3306
    protocol        = "tcp"
    security_groups = [aws_security_group.backend.id]
  }

  # Temporary internet access for installation of mariadb as I couldn't find a suitable AMI with mariadb pre-installed (TODO: remove after setup is done)
  #egress {
  #  from_port   = 0
  #  to_port     = 0
  #  protocol    = "-1"
  #  cidr_blocks = ["0.0.0.0/0"]
  #}
}

# EC2 Instances
resource "aws_instance" "frontend" {
  ami           = "ami-06650ca7ed78ff6fa" # Ubuntu 22.04 LTS
  instance_type = "t2.micro"
  subnet_id     = aws_subnet.public.id
  key_name      = var.key_name
  
  associate_public_ip_address = true
  
  vpc_security_group_ids = [aws_security_group.frontend.id]
  
  tags = {
    Name = "vaccine-frontend"
  }
}

resource "aws_instance" "backend" {
  ami           = "ami-06650ca7ed78ff6fa" # Ubuntu 22.04 LTS
  instance_type = "t2.micro"
  subnet_id     = aws_subnet.public.id
  key_name      = var.key_name
  
  associate_public_ip_address = true
  
  vpc_security_group_ids = [aws_security_group.backend.id]
  
  tags = {
    Name = "vaccine-backend"
  }
}

# MariaDB Instance
resource "aws_instance" "mariadb" {
  ami           = "ami-06650ca7ed78ff6fa" # Ubuntu 22.04 LTS
  instance_type = "t2.micro"
  subnet_id     = aws_subnet.private.id
  key_name      = var.key_name
  
  vpc_security_group_ids = [aws_security_group.mariadb.id]
  
  associate_public_ip_address = false

  # Startup script to install mariadb although it didnt work as expected
  user_data = <<-EOF
              #!/bin/bash
              # Update package list
              apt-get update

              # Install MariaDB without interactive prompts
              export DEBIAN_FRONTEND=noninteractive
              apt-get install -y mariadb-server

              # Start and enable MariaDB
              systemctl start mariadb
              systemctl enable mariadb

              # Secure MariaDB installation
              mysql -e "UPDATE mysql.user SET Password = PASSWORD('${var.db_password}') WHERE User = 'root'"
              mysql -e "DELETE FROM mysql.user WHERE User=''"
              mysql -e "DELETE FROM mysql.user WHERE User='root' AND Host NOT IN ('localhost', '127.0.0.1', '::1')"
              mysql -e "DROP DATABASE IF EXISTS test"
              mysql -e "DELETE FROM mysql.db WHERE Db='test' OR Db='test\\_%'"
              mysql -e "FLUSH PRIVILEGES"

              # Configure MariaDB to listen on all interfaces
              sed -i 's/bind-address\s*=\s*127.0.0.1/bind-address = 0.0.0.0/' /etc/mysql/mariadb.conf.d/50-server.cnf
              
              # Restart MariaDB to apply changes
              systemctl restart mariadb
              EOF
  
  tags = {
    Name = "vaccine-mariadb"
  }
}

# NAT Gateway (for private subnet internet access during setup will remove after setup)
resource "aws_eip" "nat" {
  domain = "vpc"
}

resource "aws_nat_gateway" "main" {
  allocation_id = aws_eip.nat.id
  subnet_id     = aws_subnet.public.id

  tags = {
    Name = "vaccine-nat-gateway"
  }
}

# Route Table for Private Subnet
resource "aws_route_table" "private" {
  vpc_id = aws_vpc.vaccine_vpc.id

  #route {
  #  cidr_block     = "0.0.0.0/0"
  #  nat_gateway_id = aws_nat_gateway.main.id # TODO: remove after setup is done
  #}

  tags = {
    Name = "private-rt"
  }
}

# Route Table Association for Private Subnet
resource "aws_route_table_association" "private" {
  subnet_id      = aws_subnet.private.id
  route_table_id = aws_route_table.private.id
}

# Security Group for Grafana
resource "aws_security_group" "grafana" {
  name        = "cloud-vaccine-grafana-sg"
  description = "Security group for Grafana monitoring"
  vpc_id      = aws_vpc.vaccine_vpc.id

  # Grafana Web Interface
  ingress {
    from_port   = 3000
    to_port     = 3000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # SSH Access
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Allow Prometheus to scrape metrics from backend and database
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "grafana-sg"
  }
}

# Grafana EC2 Instance
resource "aws_instance" "grafana" {
  ami           = "ami-06650ca7ed78ff6fa" # Ubuntu 22.04 LTS
  instance_type = "t2.micro"
  subnet_id     = aws_subnet.public.id
  key_name      = var.key_name

  associate_public_ip_address = true
  
  vpc_security_group_ids = [aws_security_group.grafana.id]

  root_block_device {
    volume_size = 20  # Larger volume for metrics storage
  }
  
  tags = {
    Name = "vaccine-monitoring"
  }

  # User data script to install Grafana and Prometheus
  user_data = <<-EOF
              #!/bin/bash
              # Update and install required packages
              apt-get update
              apt-get install -y apt-transport-https software-properties-common

              # Add Grafana repository
              wget -q -O /usr/share/keyrings/grafana.key https://apt.grafana.com/gpg.key
              echo "deb [signed-by=/usr/share/keyrings/grafana.key] https://apt.grafana.com stable main" | tee -a /etc/apt/sources.list.d/grafana.list

              # Install Grafana
              apt-get update
              apt-get install -y grafana

              # Install Prometheus
              apt-get install -y prometheus

              # Start and enable services
              systemctl enable grafana-server
              systemctl start grafana-server
              systemctl enable prometheus
              systemctl start prometheus

              # Install Node Exporter
              apt-get install -y prometheus-node-exporter
              systemctl enable prometheus-node-exporter
              systemctl start prometheus-node-exporter
              EOF
}

# Allow MariaDB security group to accept connections from Grafana
resource "aws_security_group_rule" "mariadb_monitoring" {
  type                     = "ingress"
  from_port               = 9104  # MySQL Exporter port
  to_port                 = 9104
  protocol                = "tcp"
  source_security_group_id = aws_security_group.grafana.id
  security_group_id       = aws_security_group.mariadb.id
}

# Allow Backend security group to accept connections from Grafana
resource "aws_security_group_rule" "backend_monitoring" {
  type                     = "ingress"
  from_port               = 8000  # FastAPI metrics endpoint
  to_port                 = 8000
  protocol                = "tcp"
  source_security_group_id = aws_security_group.grafana.id
  security_group_id       = aws_security_group.backend.id
}