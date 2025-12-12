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
                    sh "python3 --version || python --version || true"

                    // Compute a safe timestamp (never null)
                    def tsOut = sh(script: "date -u +%Y%m%dT%H%M%SZ || true", returnStdout: true).trim()
                    if (!tsOut) {
                        tsOut = new Date().format("yyyyMMdd'T'HHmmss'Z'", TimeZone.getTimeZone('UTC'))
                    }
                    env.TS = tsOut
                    echo "Build timestamp: ${env.TS}"

                    // Prepare directories
                    sh "mkdir -p ${ART_DIR} || true"
                    sh "rm -rf reports || true; mkdir -p reports"
                }
            }
        }

        stage('test') {
            steps {
                script {
                    // Create venv and install pytest inside it
                    sh '''
                        # choose python command
                        PY_CMD=python3
                        if ! command -v $PY_CMD >/dev/null 2>&1; then
                            PY_CMD=python
                        fi
                        echo "Using $PY_CMD to create venv"

                        # create venv
                        $PY_CMD -m venv venv
                        . venv/bin/activate

                        # install pytest inside venv
                        pip install --upgrade pip
                        pip install pytest

                        # run pytest
                        pytest -q --junitxml=reports/junit-${TS}.xml || true

                        echo "pytest finished at ${TS}" > reports/run-${TS}.log || true
                    '''
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
                        echo "Warning: junit XML not found: reports/junit-${env.TS}.xml"
                    }
                }
            }
        }

        stage('publish') {
            steps {
                script {
                    def tarName = "advision-artifact-${env.TS}.tar.gz"

                    // Package reports
                    sh "tar -czf ${tarName} reports || true"

                    // Ensure artifact dir exists
                    sh "mkdir -p ${ART_DIR} || true"

                    // Move to shared directory + copy to workspace for Jenkins archive
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
            sh 'echo Pipeline finished at: $(date -u) || true'
        }
    }
}
