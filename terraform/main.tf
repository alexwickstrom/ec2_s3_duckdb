provider "aws" {
  region = "us-west-2"
}

resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
}

resource "aws_subnet" "main" {
  vpc_id     = aws_vpc.main.id
  cidr_block = "10.0.1.0/24"
}

resource "aws_security_group" "allow_alb" {
  name        = "allow_alb"
  description = "Allow inbound traffic"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_db_instance" "my_db" {
  allocated_storage    = 20
  storage_type         = "gp2"
  engine               = "postgres"
  engine_version       = "15"
  instance_class       = "db.t2.micro"
  name                 = "mydb"
  username             = var.db_username
  password             = var.db_password
  parameter_group_name = "default.postgres13"
  skip_final_snapshot   = true
}

resource "aws_instance" "my_instance" {
  ami           = "ami-0c55b159cbfafe1f0" # Update this to a relevant AMI ID
  instance_type = var.instance_type

  subnet_id = aws_subnet.main.id

  security_groups = [
    aws_security_group.allow_alb.name
  ]

  provisioner "file" {
    source      = "./app/"
    destination = "/home/ubuntu/app"
  }
  
  provisioner "remote-exec" {
    inline = [
      "chmod +x /home/ubuntu/app/entrypoint.sh",
      "/home/ubuntu/app/entrypoint.sh"
    ]
  }


  user_data = <<-EOF
              #!/bin/bash
              apt-get update
              apt-get install -y python3 python3-pip
              EOF

  tags = {
    Name = "my_instance"
  }
}

resource "aws_s3_bucket" "my_bucket" {
  bucket = "my-bucket"
  acl    = "private"

  tags = {
    Name        = "my-bucket"
    Environment = "Dev"
  }
}
