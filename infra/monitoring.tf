resource "docker_image" "prometheus" {
  name = "sentiment-prometheus:latest"

  build {
    context    = abspath("${path.module}/../monitoring")
    dockerfile = "Dockerfile.prometheus"
  }

  keep_locally = true
}

resource "docker_container" "prometheus" {
  name    = "prometheus"
  image   = docker_image.prometheus.image_id
  restart = "unless-stopped"

  networks_advanced {
    name = docker_network.cicd.name
  }

  ports {
    internal = 9090
    external = 9090
  }

  command = [
    "--config.file=/etc/prometheus/prometheus.yml",
    "--storage.tsdb.retention.time=15d"
  ]
}

resource "docker_image" "grafana" {
  name         = "grafana/grafana:latest"
  keep_locally = true
}

resource "docker_container" "grafana" {
  name    = "grafana"
  image   = docker_image.grafana.image_id
  restart = "unless-stopped"

  networks_advanced {
    name = docker_network.cicd.name
  }

  ports {
    internal = 3000
    external = 3000
  }

  env = ["GF_SECURITY_ADMIN_PASSWORD=admin"]
}
