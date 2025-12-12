pipeline {
  agent {
    docker {
      image 'python:3.10'
      args '-u' // unbuffered output
    }
  }

  environment {
    ART_DIR = "/tmp/advision-logs"
  }

  stages {
    stage('init') {
      steps {
        script {
          echo "Checking python availability..."
          sh "python --version"
          // compute timestamp defensively (try date -u first, fallback to date)
          def tsOut = sh(script: "date -u +%Y%m%dT%H%M%SZ || true", returnStdout: true).trim()
          if (!tsOut) {
            tsOut = sh(script: "date +%Y%m%dT%H%M%SZ || true", returnStdout: true).trim()
          }
          if (!tsOut) {
            // final fallback to java timestamp
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
          // Use venv inside the container to ensure clean installs / no system pip confusion
          sh """
            python -m venv venv
            . venv/bin/activate
            pip install --upgrade pip
            pip install pytest
            # run pytest and produce junit xml (use env.TS)
            venv/bin/pytest -q --junitxml=reports/junit-${env.TS}.xml || true
            echo "pytest finished at ${env.TS}" > reports/run-${env.TS}.log || true
          """
        }
      }
      post {
        always {
          junit allowEmptyResults: true, testResults: "reports/junit-${env.TS}.xml"
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
            // do not fail here — tests may legitimately produce no xml; handle later if needed
          }
        }
      }
    }

    stage('publish') {
      steps {
        script {
          def tarName = "advision-artifact-${env.TS}.tar.gz"
          sh "tar -czf ${tarName} reports || true"

          // copy artifact into container's ART_DIR (this directory should be mounted to your host)
          sh "mkdir -p ${ART_DIR} || true"
          sh "mv -f ${tarName} ${ART_DIR}/${tarName} || true"

          // ensure a copy exists in the workspace so Jenkins' archiveArtifacts sees it
          sh "cp ${ART_DIR}/${tarName} . || true"
          archiveArtifacts artifacts: "${tarName}", fingerprint: true

          echo "Artifacts copied to ${ART_DIR}/${tarName}"
        }
      }
    }
  }

  post {
    always {
      sh "echo Pipeline finished at: \$(date -u) || true"
    }
  }
}
