provider "aws" {
  region = "us-east-1"
}

resource "aws_instance" "devops" {
  ami           = "ami-12345678"
  instance_type = "t2.micro"
}
