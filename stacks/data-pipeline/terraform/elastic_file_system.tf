resource "aws_efs_file_system" "data_pipeline" {
  creation_token = "practice-migrations"

  tags = {
    Name = "PracticeMigrationFileSystem"
  }
}