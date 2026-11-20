terraform {
  required_version = ">= 1.5.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# -------------------------------------------------------------
# 1. ALMACENAMIENTO: BUCKET RAW (ARCHIVOS CRUDOS DE ENTRADA)
# -------------------------------------------------------------
resource "google_storage_bucket" "raw_bucket" {
  name                     = "${var.bucket_raw_name}-${var.environment}"
  location                 = var.region
  force_destroy            = true
  uniform_bucket_level_access = true

  versioning {
    enabled = false
  }

  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      age = 90 # Depuracion automatica de logs crudos tras 90 dias
    }
  }

  labels = {
    entorno = var.environment
    servicio = "fitpulse-ingesta"
    materia  = "computo-en-la-nube"
  }
}

# -------------------------------------------------------------
# 2. ALMACENAMIENTO: BUCKET CLEAN (DATASETS LIMPIOS Y MODELOS)
# -------------------------------------------------------------
resource "google_storage_bucket" "clean_bucket" {
  name                     = "${var.bucket_clean_name}-${var.environment}"
  location                 = var.region
  force_destroy            = true
  uniform_bucket_level_access = true

  versioning {
    enabled = true # Versionamiento activo para reproducibilidad de modelos ML
  }

  labels = {
    entorno = var.environment
    servicio = "fitpulse-analytics"
    materia  = "analitica-de-datos"
  }
}

# -------------------------------------------------------------
# 3. MIDDLEWARE DE MENSAJERIA: TOPICO Y SUSCRIPCION PUB/SUB
# -------------------------------------------------------------
resource "google_pubsub_topic" "ingesta_topic" {
  name = "${var.pubsub_topic_name}-${var.environment}"

  labels = {
    entorno = var.environment
    servicio = "fitpulse-pipeline"
  }
}

resource "google_pubsub_subscription" "worker_subscription" {
  name  = "fitpulse-worker-clean-sub"
  topic = google_pubsub_topic.ingesta_topic.name

  # Retencion de mensajes no reconocidos durante 7 dias
  message_retention_duration = "604800s"
  retain_acked_messages      = false
  ack_deadline_seconds       = 60

  expiration_policy {
    ttl = "2678400s" # 31 dias
  }
}

# -------------------------------------------------------------
# 4. GESTION DE IDENTIDAD Y ACCESO: SERVICE ACCOUNT CON MINIMO PRIVILEGIO
# -------------------------------------------------------------
resource "google_service_account" "app_sa" {
  account_id   = "fitpulse-sa-${var.environment}"
  display_name = "Service Account Minimo Privilegio para FitPulse Backend y Worker"
  description  = "Solo cuenta con acceso de lectura en raw, lectura/escritura en clean y publicacion en PubSub"
}

# Permiso estricto sobre el bucket raw (lectura de archivos)
resource "google_storage_bucket_iam_member" "sa_raw_viewer" {
  bucket = google_storage_bucket.raw_bucket.name
  role   = "roles/storage.objectViewer"
  member = "serviceAccount:${google_service_account.app_sa.email}"
}

# Permiso estricto sobre el bucket clean (creacion y versionamiento de limpios)
resource "google_storage_bucket_iam_member" "sa_clean_admin" {
  bucket = google_storage_bucket.clean_bucket.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.app_sa.email}"
}

# Permiso de publicacion y consumo en Pub/Sub
resource "google_pubsub_topic_iam_member" "sa_pubsub_publisher" {
  topic  = google_pubsub_topic.ingesta_topic.name
  role   = "roles/pubsub.publisher"
  member = "serviceAccount:${google_service_account.app_sa.email}"
}

resource "google_pubsub_subscription_iam_member" "sa_pubsub_subscriber" {
  subscription = google_pubsub_subscription.worker_subscription.name
  role         = "roles/pubsub.subscriber"
  member       = "serviceAccount:${google_service_account.app_sa.email}"
}
