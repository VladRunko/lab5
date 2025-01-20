pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE = 'my-flask-app'
        DOCKER_TAG = 'latest'
    }

    stages {
        stage('Checkout') {
            steps {
                git url: 'https://github.com/VladRunko/lab5.git', branch: 'main'
            }
        }

        stage('Build') {
            steps {
                echo 'Building the project...'

                script {
                    sh 'docker build -t $DOCKER_IMAGE:$DOCKER_TAG .'
                }
            }
        }

        stage('Deploy') {
            steps {
                echo 'Deploying the project...'

                script {
                    sh 'docker run -d -p 5001:5000 $DOCKER_IMAGE:$DOCKER_TAG'
                }
            }
        }
    }

    post {
        always {
            echo 'Pipeline completed.'
        }
        success {
            echo 'Deployment successful!'
        }
        failure {
            echo 'Deployment failed.'
        }
    }
}
