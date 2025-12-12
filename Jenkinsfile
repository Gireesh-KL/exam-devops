pipeline {
  agent any

  environment {
    ART_DIR = "/tmp/advision-logs"
  }

  stages {
    stage('init') {
      steps {
        script {
          echo "Checking python availability..."
          sh "python3 --version || python --version"
          // compute timestamp defensively
          def tsOut = sh(script: "date -u +%Y%m%dT%H%M%SZ || true", returnStdout: true).trim()
          if (!tsOut) {
            tsOut = sh(script: "date +%Y%m%dT%H%M%SZ || true", returnStdout: true).trim()
          }
          if (!tsOut) {
            tsOut = new Date().format("yyyyMMdd'T'HHmmss'Z'", TimeZone.getTimeZone('UTC'))
          }
          env.TS = tsOut
          echo "Build timestamp: ${env.TS}"

          sh "mkdir -p ${ART_DIR} || true"
          sh "rm -rf reports || true; mkdir -p reports"
        }
      }
    }

    stage('test') {
      steps {
        script {
          // create venv and install pytest inside it; avoids system pip issues (PEP 668)
          sh '''
            # prefer python3, fall back to python
            PY_CMD=python3
            if ! command -v $PY_CMD >/dev/null 2>&1; then
              PY_CMD=python
            fi
            echo "Using $PY_CMD to create venv"
            $PY_CMD -m venv venv
            . venv/bin/activate
            pip install --upgrade pip
            pip install pytest
            pytest -q --junitxml=reports/junit-${TS}.xml || true
            echo "pytest finished at ${TS}" > reports/run-${TS}.log || true
          '''
        }
      }
      post {
        always {
          junit allowEmptyResults: true, testResults: "reports/junit-${TS}.xml"
          archiveArtifacts artifacts: "reports/**", fingerprint: true
        }
      }
    }

    stage('verify') {
      steps {
        script {
          sh "ls -la reports || true"
          if (!fileExists("reports/junit-${env.TS}.xml")) {
            echo "Warning: junit xml not found: reports/junit-${env.TS}.xml"
          }
        }
      }
    }

    stage('publish') {
      steps {
        script {
          def tarName = "advision-artifact-${env.TS}.tar.gz"
          sh "tar -czf ${tarName} reports || true"
          sh "mkdir -p ${ART_DIR} || true"
          sh "mv -f ${tarName} ${ART_DIR}/${tarName} || true"
          sh "cp ${ART_DIR}/${tarName} . || true"
          archiveArtifacts artifacts: "${tarName}", fingerprint: true
          echo "Artifacts copied to ${ART_DIR}/${tarName}"
        }
      }
    }
  }

  post {
    always {
      sh "echo Pipeline finished at: $(date -u) || true"
    }
  }
}
