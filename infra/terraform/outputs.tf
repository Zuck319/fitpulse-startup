output "raw_bucket_name" {
  description = "Nombre del bucket de Cloud Storage para datos crudos"
  value       = google_storage_bucket.raw_bucket.name
}

output "raw_bucket_url" {
  description = "URI gs:// del bucket raw"
  value       = google_storage_bucket.raw_bucket.url
}

output "clean_bucket_name" {
  description = "Nombre del bucket de Cloud Storage para datos limpios"
  value       = google_storage_bucket.clean_bucket.name
}

output "clean_bucket_url" {
  description = "URI gs:// del bucket clean"
  value       = google_storage_bucket.clean_bucket.url
}

output "pubsub_topic_id" {
  description = "Identificador del topico de Pub/Sub para ingesta de accesos"
  value       = google_pubsub_topic.ingesta_topic.id
}

output "pubsub_subscription_id" {
  description = "Identificador de la suscripcion de Pub/Sub para el worker serverless"
  value       = google_pubsub_subscription.worker_subscription.id
}

output "service_account_email" {
  description = "Correo del Service Account con minimo privilegio asignado"
  value       = google_service_account.app_sa.email
}
