# resource "tls_private_key" "app" {
#   algorithm = "RSA"
#   rsa_bits  = 4096
# }

# resource "aws_key_pair" "app" {
#   key_name   = "${var.app_name}-key"
#   public_key = tls_private_key.app.public_key_openssh
# }

# resource "local_file" "private_key" {
#   content         = tls_private_key.app.private_key_pem
#   filename        = "${path.module}/${var.app_name}.pem"
#   file_permission = "0400"
# }


# # EC2 instance
# data "aws_ami" "amazon_linux" {
#   most_recent = true
#   owners      = ["amazon"]

#   filter {
#     name   = "name"
#     values = ["al2023-ami-*-x86_64"]
#   }

#   filter {
#     name   = "virtualization-type"
#     values = ["hvm"]
#   }
# }

# resource "aws_instance" "app" {
#   ami                    = data.aws_ami.amazon_linux.id
#   instance_type          = "t3.micro"
#   subnet_id              = aws_subnet.public.id
#   vpc_security_group_ids = [aws_security_group.app.id]
#   key_name               = aws_key_pair.app.key_name
#   user_data              = file("${path.module}/user_data.sh")

#   tags = { Name = var.app_name }

#   connection {
#     type        = "ssh"
#     user        = "ec2-user"
#     private_key = tls_private_key.app.private_key_pem
#     host        = self.public_ip
#   }

#   # Wait for user_data (Docker install) to finish
#   provisioner "remote-exec" {
#     inline = ["cloud-init status --wait"]
#   }

#   # -------------------- copy files ------------------
#   provisioner "remote-exec" {
#     inline = ["mkdir -p ${var.app_dir}"]
#   }

#   provisioner "file" {
#     source      = "${path.module}/../docker"
#     destination = "${var.app_dir}/docker"
#   }

#   provisioner "file" {
#     source      = "${path.module}/../src"
#     destination = "${var.app_dir}/src"
#   }

#   provisioner "file" {
#     source      = "${path.module}/../pyproject.toml"
#     destination = "${var.app_dir}/pyproject.toml"
#   }

#   # Build and start the app
#   provisioner "remote-exec" {
#     inline = [
#       "cd ${var.app_dir}",
#       "docker compose -f docker/docker-compose.yml up -d --build",
#     ]
#   }
# }

# output "public_ip" {
#   value = aws_instance.app.public_ip
# }

# output "ssh_command" {
#   value = "ssh -i ${local_file.private_key.filename} ec2-user@${aws_instance.app.public_ip}"
# }

# output "app_url" {
#   value = "http://${aws_instance.app.public_ip}:8000"
# }
