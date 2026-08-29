pipeline {
  agent any
  options { timestamps(); disableConcurrentBuilds(); timeout(time: 90, unit: 'MINUTES') }
  parameters {
    choice(name: 'DEPLOY_TARGET', choices: ['none', 'kind', 'gke'], description: 'Explicit deployment target')
    string(name: 'GCP_PROJECT', defaultValue: 'dynamic-agentic-bot-dev')
    string(name: 'GCP_REGION', defaultValue: 'us-central1')
    string(name: 'GKE_CLUSTER', defaultValue: 'dynamic-agentic')
    string(name: 'ARTIFACT_REPOSITORY', defaultValue: 'dynamic-agentic')
  }
  environment {
    NEXT_TELEMETRY_DISABLED = '1'
    IMAGE_TAG = "${GIT_COMMIT}"
  }
  stages {
    stage('Checkout') { steps { checkout scm; script { env.IMAGE_TAG = sh(returnStdout: true, script: 'git rev-parse HEAD').trim() } } }
    stage('Backend dependencies') { steps { sh 'uv sync --project apps/api --all-groups --locked' } }
    stage('Backend lint') { steps { sh 'uv run --project apps/api ruff check apps/api/src tests/backend && uv run --project apps/api ruff format --check apps/api/src tests/backend' } }
    stage('Backend typecheck') { steps { sh 'uv run --project apps/api mypy --config-file apps/api/pyproject.toml apps/api/src' } }
    stage('Backend tests') { steps { sh 'uv run --project apps/api pytest tests/backend' } }
    stage('Frontend install') { steps { sh 'npm ci --prefix apps/web' } }
    stage('Frontend lint') { steps { sh 'npm run lint --prefix apps/web' } }
    stage('Frontend typecheck') { steps { sh 'npm run typecheck --prefix apps/web' } }
    stage('Frontend build') { steps { sh 'npm run build --prefix apps/web' } }
    stage('Security and dependency checks') {
      steps {
        sh 'npm audit --prefix apps/web --audit-level=high'
        sh 'docker run --rm -v "$WORKSPACE:/src" aquasec/trivy:0.69.1 fs --exit-code 1 --severity HIGH,CRITICAL --ignore-unfixed /src'
      }
    }
    stage('Docker build') {
      steps {
        sh 'docker build --pull -f apps/api/Dockerfile -t dynamic-agentic-backend:$IMAGE_TAG .'
        sh 'docker build --pull -f apps/web/Dockerfile -t dynamic-agentic-frontend:$IMAGE_TAG .'
      }
    }
    stage('Image vulnerability scan') {
      steps {
        sh 'docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy:0.69.1 image --exit-code 1 --severity CRITICAL --ignore-unfixed dynamic-agentic-backend:$IMAGE_TAG'
        sh 'docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy:0.69.1 image --exit-code 1 --severity CRITICAL --ignore-unfixed dynamic-agentic-frontend:$IMAGE_TAG'
      }
    }
    stage('Helm lint and template') {
      steps {
        sh 'helm lint deploy/helm/dynamic-agentic -f deploy/helm/dynamic-agentic/values-kind.yaml'
        sh 'helm lint deploy/helm/observability'
        sh 'helm template dynamic-agentic deploy/helm/dynamic-agentic -f deploy/helm/dynamic-agentic/values-kind.yaml >/dev/null'
      }
    }
    stage('Push immutable images') {
      when { expression { params.DEPLOY_TARGET == 'gke' } }
      steps {
        sh '''
          set +x
          registry="${GCP_REGION}-docker.pkg.dev/${GCP_PROJECT}/${ARTIFACT_REPOSITORY}"
          gcloud auth configure-docker "${GCP_REGION}-docker.pkg.dev" --quiet
          docker tag "dynamic-agentic-backend:${IMAGE_TAG}" "$registry/backend:${IMAGE_TAG}"
          docker tag "dynamic-agentic-frontend:${IMAGE_TAG}" "$registry/frontend:${IMAGE_TAG}"
          docker push "$registry/backend:${IMAGE_TAG}"
          docker push "$registry/frontend:${IMAGE_TAG}"
        '''
      }
    }
    stage('Deploy') {
      when { expression { params.DEPLOY_TARGET != 'none' } }
      steps {
        sh '''
          if [ "$DEPLOY_TARGET" = kind ]; then
            deploy/scripts/kind-deploy.sh "$IMAGE_TAG"
          else
            deploy/scripts/gke-deploy.sh "$IMAGE_TAG"
          fi
        '''
      }
    }
    stage('Rollout verification') {
      when { expression { params.DEPLOY_TARGET != 'none' } }
      steps {
        sh 'kubectl -n dynamic-agentic rollout status deployment/dynamic-agentic-backend --timeout=10m'
        sh 'kubectl -n dynamic-agentic rollout status deployment/dynamic-agentic-frontend --timeout=10m'
      }
    }
    stage('Smoke tests') {
      when { expression { params.DEPLOY_TARGET != 'none' } }
      steps { sh 'deploy/scripts/smoke-test.sh' }
    }
  }
  post {
    failure {
      sh 'kubectl -n dynamic-agentic get pods 2>/dev/null || true'
      echo 'Deployment did not pass readiness; use helm history and the documented rollback command.'
    }
  }
}
