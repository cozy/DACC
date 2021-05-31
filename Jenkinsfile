pipeline {

  agent {
    label 'docker'
  }

  options {
    disableConcurrentBuilds()
    gitLabConnection('https://gitlab.cozycloud.cc')
    gitlabBuilds(builds: ["Build", "Test", "Deploy"])
  }

  stages {

    stage ('Build') {
      steps {
        gitlabCommitStatus("Build") {
          echo 'Building....'
          mattermostSend(color: "warning", channel: "feat---dacc", message: "DACC build, test & deploy on **dev**: <${env.BUILD_URL}|build ${env.BUILD_NUMBER}> triggered by ${env.gitlabUserName}")
          sh "sudo rm -rf sandbox"
          deleteDir()
          dir('sandbox/') {
            checkout scm
            sh '''
              echo "FLASK_ENV=development" > .env
              echo "PORT=5000" >> .env
              cp config-template.yml config.yml
              docker-compose -p dacc build
            '''
            sh '''
              docker-compose -p dacc up -d
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
        gitlabCommitStatus("Deploy") {
          echo 'Deploying....'
          dir('sandbox/') {
            sh '''
              ssh -o StrictHostkeyChecking=no jenkins@dacc-01-dev hostname -f
              ssh -o StrictHostkeyChecking=no jenkins@dacc-01-dev sudo /usr/local/sbin/deploy-dacc-branch.sh master
            '''
          }
        }
      }
    }

  }
  post {
    failure {
      mattermostSend(color: "danger", channel: "feat---dacc", message: "DACC build, test & deploy <${env.BUILD_URL}|build ${env.BUILD_NUMBER}> failed")
    }
    success {
      mattermostSend(color: "good", channel: "feat---dacc", message: "DACC build, test & deploy <${env.BUILD_URL}|build ${env.BUILD_NUMBER}> succeeded")
    }
    aborted {
      mattermostSend(color: "#000000", channel: "feat---dacc", message: "DACC build, test & deploy <${env.BUILD_URL}|build ${env.BUILD_NUMBER}> aborted")
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
