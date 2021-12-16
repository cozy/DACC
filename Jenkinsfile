pipeline {

  agent {
    label 'docker'
  }

  options {
    disableConcurrentBuilds()
    gitLabConnection('https://gitlab.cozycloud.cc')
    gitlabBuilds(builds: ["Lint", "Build", "Test"])
  }

  stages {

    stage ('Setup') {
      steps {
        echo 'Setting up....'
        sh "sudo rm -rf sandbox"
        deleteDir()
        dir('sandbox/') {
          checkout scm
          sh '''
            echo "FLASK_ENV=development" > .env
            echo "FLASK_RUN_HOST=0.0.0.0" >> .env
            echo "FLASK_PORT=5000" >> .env
            echo "PORT=5000" >> .env
            cp config-template.yml config.yml
          '''
        }
      }
    }

    stage ('Build') {
      steps {
        gitlabCommitStatus("Build") {
          echo 'Building....'
          dir('sandbox/') {
            sh '''
              docker-compose -p dacc build
            '''
            sh '''
              docker-compose -p dacc up -d
            '''
            sh '''
              docker exec dacc_web flask reset-all-tables --yes
              docker exec dacc_web flask insert-definitions-json
            '''
          }
        }
      }
    }

    stage ('Lint') {
      steps {
        gitlabCommitStatus("Lint") {
          echo 'Linter check....'
          dir('sandbox/') {
            sh '''
              docker exec dacc_web pip install black
              docker exec dacc_web black --check --diff --color .
            '''
          }
        }
      }
    }

    stage ('Test') {
      steps {
        gitlabCommitStatus("Test") {
          echo 'Testing....'
          dir('sandbox/') {
            sh '''
              docker exec dacc_web pytest
            '''
            sh '''
              curl -i http://localhost:5000/status
              test "$(curl -s http://localhost:5000/status | jq -r .global_status)" = "ok"
            '''
          }
        }
      }
    }

    stage ('Deploy') {
      steps {
        script {
          if (gitlabActionType == "PUSH" && gitlabBranch == "master")  {
            mattermostSend(color: "warning", channel: "feat---dacc", message: "DACC build, test & deploy on **dev**: <${env.BUILD_URL}|build ${env.BUILD_NUMBER}> triggered by ${env.gitlabUserName}")
            gitlabCommitStatus("Deploy") {
              echo 'Deploying....'
              dir('sandbox/') {
                sh '''
                  ssh -o StrictHostkeyChecking=no jenkins@dacc-01-dev hostname -f
                  ssh -o StrictHostkeyChecking=no jenkins@dacc-01-dev sudo /usr/local/sbin/deploy-dacc-branch.sh master
                '''
              }
            }
          } else {
            sh '''
            echo "No deploy on merge requests or non-master branches"
            '''
          }
        }
      }
    }
  }
  post {
    failure {
      mattermostSend(color: "danger", channel: "feat---dacc", message: "DACC build, test & deploy on **dev** <${env.BUILD_URL}|build ${env.BUILD_NUMBER}> failed")
    }
    success {
      script {
        if (gitlabActionType == "PUSH" && gitlabBranch == "master")  {
          mattermostSend(color: "good", channel: "feat---dacc", message: "DACC build, test & deploy on **dev**  <${env.BUILD_URL}|build ${env.BUILD_NUMBER}> succeeded")
        }
      }
    }
    aborted {
      mattermostSend(color: "#000000", channel: "feat---dacc", message: "DACC build, test & deploy on **dev**  <${env.BUILD_URL}|build ${env.BUILD_NUMBER}> aborted")
    }
    cleanup {
      dir('sandbox/') {
        sh "docker-compose -p dacc down -v --rmi all --remove-orphans"
      }
      sh "sudo rm -rf sandbox"
      /* clean up our workspace */
      cleanWs()
    }
  }
}
