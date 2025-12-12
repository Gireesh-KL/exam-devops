pipeline {
    agent any

    environment {
        // will be set in init stage
        TS = ""
        ART_DIR = "/tmp/advision-logs"
    }

    stages {
        stage('init') {
            steps {
                script {
                    // Confirm python3 availability
                    echo "Checking python3 availability..."
                    def pyCheck = sh(script: "which python3 >/dev/null 2>&1 && python3 --version || true", returnStdout: true).trim()
                    if (!pyCheck) {
                        error("python3 not found on agent. Please install python3.")
                    } else {
                        echo "python3 present: ${pyCheck}"
                    }

                    // create timestamp (UTC ISO-like) and set into env.TS
                    env.TS = sh(script: "date -u +%Y%m%dT%H%M%SZ", returnStdout: true).trim()
                    echo "Build timestamp: ${env.TS}"

                    // ensure artifact dir exists on agent
                    sh "mkdir -p ${env.ART_DIR}"
                }
            }
        }

        stage('test') {
            steps {
                script {
                    // Create a reports directory
                    sh "rm -rf reports || true; mkdir -p reports"

                    // Ensure dependencies installed (only pytest here)
                    sh "python3 -m pip --version || true"
                    sh "python3 -m pip install --user pytest || true"

                    // Run tests and generate junit xml (timestamped)
                    sh """
                      python3 -m pytest -q --junitxml=reports/junit-${env.TS}.xml || true
                    """

                    // Save console output to a log file (optional)
                    sh "echo 'pytest finished at $(date -u)' > reports/run-${env.TS}.log || true"
                }
            }
            post {
                always {
                    // Publish junit results to Jenkins
                    junit allowEmptyResults: true, testResults: "reports/junit-${env.TS}.xml"
                    archiveArtifacts artifacts: "reports/**", fingerprint: true
                }
            }
        }

        stage('verify') {
            steps {
                script {
                    // Put any static verification here (lint, small static checks). Example: ensure tests produced a junit xml.
                    if (!fileExists("reports/junit-${env.TS}.xml")) {
                        echo "Warning: junit xml not found: reports/junit-${env.TS}.xml"
                        // depending on policy, you can fail:
                        // error("No junit test results produced.")
                    } else {
                        echo "JUnit results present."
                    }
                }
            }
        }

        stage('publish') {
            steps {
                script {
                    // create a timestamped tarball of reports and workspace artifacts
                    def tarName = "advision-artifact-${env.TS}.tar.gz"
                    sh """
                      tar -czf ${tarName} reports || true
                      mkdir -p ${ART_DIR}
                      mv -f ${tarName} ${ART_DIR}/${tarName}
                      echo "Artifacts copied to ${ART_DIR}/${tarName}"
                    """

                    // Also archive artifact into Jenkins UI (archives must be in workspace path)
                    archiveArtifacts artifacts: "${ART_DIR}/${tarName}", allowEmptyArchive: false, fingerprint: true
                }
            }
        }
    } // stages

    post {
        always {
            echo "Pipeline finished at: ${sh(script: 'date -u', returnStdout: true).trim()}"
        }
    }
}
