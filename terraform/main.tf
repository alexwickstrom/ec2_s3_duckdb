resource "aws_key_pair" "dev_env_auth" {
  key_name   = "mtc_dev_key"
  public_key = file("~/.ssh/mtc_dev_key.pub")
}

provider "aws" {
  region = "us-west-2"
}

resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
}

resource "aws_subnet" "main" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "us-west-2c"
  map_public_ip_on_launch = true
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
  engine_version       = "12"
  instance_class       = "db.t2.micro"
  db_name              = "mydb"
  username             = var.db_username
  password             = var.db_password
  parameter_group_name = "default.postgres12"
  skip_final_snapshot  = true
}
output "rds_endpoint" {
  value = aws_db_instance.my_db.endpoint
}

resource "aws_instance" "my_instance" {
  ami                         = "ami-001e998553e998c5c" # can play with different AMIs
  instance_type               = var.instance_type
  key_name                    = aws_key_pair.dev_env_auth.id
  subnet_id                   = aws_subnet.main.id
  associate_public_ip_address = true
  vpc_security_group_ids = [
    aws_security_group.allow_alb.id
  ]
  availability_zone = "us-west-2c"

  user_data = <<-EOF
              #!/bin/bash
              apt-get update
              apt-get install -y python3 python3-pip
              EOF

  connection {
    type        = "ssh"
    user        = "ec2-user"
    host        = self.public_ip
    private_key = file("${var.private_key}")
  }

  tags = {
    Name = "my_instance"
  }
}

output "instance_public_ip" {
  value       = aws_instance.my_instance.public_ip
  description = "The public IP address to SSH into the EC2 instance."
}

output "instance_public_dns" {
  value       = aws_instance.my_instance.public_dns
  description = "The public DNS to SSH into the EC2 instance."
}

# resource "time_sleep" "wait_10_seconds" {
#   depends_on = [aws_instance.my_instance]

#   create_duration = "10s"
# }

# resource "null_resource" "post_provision" {
#   depends_on = [aws_instance.my_instance, time_sleep.wait_10_seconds]
#     triggers = {
#       instance_dns = aws_instance.my_instance.public_dns
#     }

#   provisioner "file" {
#     source      = "./app/"
#     destination = "/home/ubuntu/app"

#     connection {
#       type        = "ssh"
#       host        = aws_instance.my_instance.public_dns
#       user        = "ubuntu"
#       private_key = file("~/.ssh/id_rsa")
#     }
#   }

#   provisioner "remote-exec" {

#     inline = [
#       "chmod +x /home/ubuntu/app/entrypoint.sh",
#       "/home/ubuntu/app/entrypoint.sh"
#     ]

#     connection {
#       type        = "ssh"
#       host        = aws_instance.my_instance.public_dns
#       user        = "ubuntu"
#       private_key = file("~/.ssh/id_rsa")
#     }
#   }
# }
# resource "aws_s3_bucket" "my_bucket" {
#   bucket = "my-parquet-bucket-a9b8c7"
#   acl    = "private"

#   tags = {
#     Name        = "my-parquet-bucket-a9b8c7"
#     Environment = "Dev"
#   }
# }
