// Jenkinsfile - Pipeline CI/CD SentimentAI - TP4 Terraform & IaC

pipeline {
    agent any

    environment {
        IMAGE_NAME = 'sentiment-ai'
        REGISTRY = 'ghcr.io/mohamadjaafarassaf1994'
        IMAGE_TAG = sh(script: 'git rev-parse --short HEAD', returnStdout: true).trim()
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                echo "Branch: ${env.BRANCH_NAME}"
                echo "Git branch: ${env.GIT_BRANCH}"
                echo "Commit: ${env.GIT_COMMIT}"
                echo "Image tag: ${env.IMAGE_TAG}"
                sh 'git log --oneline -5'
            }
        }

        stage('Lint') {
            steps {
                sh '''
                    docker run --rm \
                    --volumes-from jenkins \
                    -w "$WORKSPACE" \
                    python:3.12-slim \
                    sh -c "pip install flake8 -q && flake8 src/ --max-line-length=100"
                '''
            }
        }

        stage('IaC Validate') {
            steps {
                dir('infra') {
                    sh 'terraform init -backend=false -input=false'
                    sh 'terraform fmt -check'
                    sh 'terraform validate'
                }
            }
        }

        stage('Build & Test') {
            steps {
                sh '''
                docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .

                docker rm -f test-runner 2>/dev/null || true

                set +e
                docker run \
                    -e CI=true \
                    --name test-runner \
                    ${IMAGE_NAME}:${IMAGE_TAG} \
                    pytest tests/ -v \
                    --cov=src \
                    --cov-report=xml:/tmp/coverage.xml \
                    --cov-report=term-missing \
                    --cov-fail-under=70
                TEST_EXIT_CODE=$?
                set -e

                docker cp test-runner:/tmp/coverage.xml ./coverage.xml 2>/dev/null || true
                sed -i "s#/app/src#${WORKSPACE}/src#g" coverage.xml || true
                docker rm -f test-runner 2>/dev/null || true

                exit $TEST_EXIT_CODE
                '''
            }
            post {
                failure {
                    echo 'Tests échoués ou coverage insuffisant (< 70%)'
                }
            }
        }

        stage('SonarQube Analysis') {
            environment {
                SONARQUBE_TOKEN = credentials('sonar-token')
            }
            steps {
                withSonarQubeEnv('sonarqube') {
                    sh '''
                    docker run --rm \
                        --network cicd-network \
                        --volumes-from jenkins \
                        -w "$WORKSPACE" \
                        -e SONAR_HOST_URL="$SONAR_HOST_URL" \
                        -e SONAR_TOKEN="$SONARQUBE_TOKEN" \
                        sonarsource/sonar-scanner-cli:latest \
                        sonar-scanner \
                        -Dsonar.projectKey=sentiment-ai \
                        -Dsonar.projectName=SentimentAI \
                        -Dsonar.projectBaseDir="$WORKSPACE" \
                        -Dsonar.sources=src \
                        -Dsonar.python.version=3.11 \
                        -Dsonar.python.coverage.reportPaths=coverage.xml \
                        -Dsonar.sourceEncoding=UTF-8 \
                        -Dsonar.scanner.metadataFilePath=$WORKSPACE/report-task.txt
                    '''
                }
            }
        }

        stage('Quality Gate') {
            steps {
                timeout(time: 15, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }

        stage('Security Scan') {
            steps {
                sh '''
                docker run --rm \
                    -v /var/run/docker.sock:/var/run/docker.sock \
                    -v trivy-cache:/root/.cache/trivy \
                    aquasec/trivy:latest image \
                    --severity HIGH,CRITICAL \
                    --exit-code 0 \
                    --format table \
                    ${IMAGE_NAME}:${IMAGE_TAG}
                '''
            }
            post {
                failure {
                    echo 'Vulnérabilités CRITICAL ou HIGH détectées !'
                    echo 'Corrigez les dépendances avant de déployer.'
                }
            }
        }

        stage('Push') {
            when {
                anyOf {
                    branch 'main'
                    expression { env.GIT_BRANCH == 'origin/main' }
                    expression { env.GIT_BRANCH == 'main' }
                }
            }
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'github-token',
                    usernameVariable: 'REGISTRY_USER',
                    passwordVariable: 'REGISTRY_PASS'
                )]) {
                    sh '''
                        echo "$REGISTRY_PASS" | docker login ghcr.io -u "$REGISTRY_USER" --password-stdin
                        docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}
                        docker push ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}
                        docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${REGISTRY}/${IMAGE_NAME}:latest
                        docker push ${REGISTRY}/${IMAGE_NAME}:latest
                    '''
                }
            }
        }

        stage('IaC Apply') {
            when {
                anyOf {
                    branch 'main'
                    expression { env.GIT_BRANCH == 'origin/main' }
                    expression { env.GIT_BRANCH == 'main' }
                }
            }
            steps {
                dir('infra') {
                    sh '''
                    terraform init -input=false

                    if docker network inspect cicd-network >/dev/null 2>&1; then
                        NETWORK_ID=$(docker network inspect cicd-network --format '{{.Id}}')
                        terraform import \
                            -var='docker_host=unix:///var/run/docker.sock' \
                            docker_network.cicd "$NETWORK_ID" 2>/dev/null || true
                    fi

                    docker rm -f sentiment-staging prometheus grafana 2>/dev/null || true

                    terraform apply -auto-approve \
                        -var='docker_host=unix:///var/run/docker.sock' \
                        -var="image_tag=${IMAGE_TAG}"
                    '''
                }
            }
        }

        stage('Deploy Staging') {
            when {
                anyOf {
                    branch 'main'
                    expression { env.GIT_BRANCH == 'origin/main' }
                    expression { env.GIT_BRANCH == 'main' }
                }
            }
            steps {
                echo "Vérification du déploiement staging Terraform..."
                sh '''
                sleep 5
                docker exec sentiment-staging curl -f http://localhost:8000/health
                '''
            }
        }

        stage('Smoke Test') {
            when {
                anyOf {
                    branch 'main'
                    expression { env.GIT_BRANCH == 'origin/main' }
                    expression { env.GIT_BRANCH == 'main' }
                }
            }
            steps {
                sh '''
                echo "Attente du démarrage (10s)..."
                sleep 10

                echo "1. Vérification de l'application SentimentAI"
                docker run --rm --network cicd-network curlimages/curl:8.5.0 \
                -f http://sentiment-staging:8000/health
                echo "/health OK"

                echo "2. Vérification des métriques applicatives"
                docker run --rm --network cicd-network curlimages/curl:8.5.0 \
                -s http://sentiment-staging:8000/metrics | grep -q sentiment_predictions_total
                echo "/metrics OK"

                echo "3. Attente du scrape Prometheus..."
                sleep 20

                echo "4. Vérification du target Prometheus sentiment-ai"
                docker run --rm --network cicd-network curlimages/curl:8.5.0 \
                -s 'http://prometheus:9090/api/v1/query?query=up%7Bjob%3D%22sentiment-ai%22%7D' | \
                grep -q '"value":\\[.*,"1"\\]'
                echo "Prometheus scrape OK"

                echo "5. Vérification de Grafana"
                docker run --rm --network cicd-network curlimages/curl:8.5.0 \
                -f http://grafana:3000/api/health
                echo "Grafana OK"
                '''
            }
            post {
                failure {
                    sh '''
                    echo "Smoke Test KO -- logs de diagnostic"
                    docker logs prometheus || true
                    docker logs sentiment-staging || true
                    docker logs grafana || true
                    '''
                }
            }
        }
    }

    post {
        always {
            sh 'docker rm -f test-runner 2>/dev/null || true'
        }
        success {
            echo "Pipeline réussi ! Image : ${env.REGISTRY}/${env.IMAGE_NAME}:${env.IMAGE_TAG}"
        }
        failure {
            echo 'Pipeline échoué. Consultez les logs ci-dessus.'
        }
    }
}
