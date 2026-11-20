variable "project_id" {
  description = "Identificador del proyecto en Google Cloud Platform"
  type        = string
  default     = "fitpulse-startup-prod"
}

variable "region" {
  description = "Region principal para el despliegue de recursos en la nube"
  type        = string
  default     = "us-central1"
}

variable "environment" {
  description = "Ambiente de ejecucion (dev, staging, production)"
  type        = string
  default     = "production"
}

variable "bucket_raw_name" {
  description = "Nombre del bucket para ingesta de archivos crudos sin procesar"
  type        = string
  default     = "fitpulse-raw-accesos"
}

variable "bucket_clean_name" {
  description = "Nombre del bucket para almacenamiento de datasets depurados y listos para ML"
  type        = string
  default     = "fitpulse-clean-accesos"
}

variable "pubsub_topic_name" {
  description = "Nombre del topico de Pub/Sub para eventos asincronos de torniquete"
  type        = string
  default     = "fitpulse-ingesta-eventos"
}
