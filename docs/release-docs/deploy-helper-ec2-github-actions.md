```markdown

    name: Simple Deploy

on:
push:
branches: [ main ]

jobs:
deploy:
runs-on: ubuntu-latest
steps:
- name: Checkout code
uses: actions/checkout@v4

      - name: Setup SSH
        run: |
          mkdir -p ~/.ssh
          echo "${{ secrets.EC2_SSH_KEY }}" > ~/.ssh/id_rsa
          chmod 600 ~/.ssh/id_rsa
          # This line prevents the "Host key verification failed" error
          ssh-keyscan -H ${{ secrets.EC2_HOST }} >> ~/.ssh/known_hosts

      - name: Run Deploy Commands
        run: |
          ssh ubuntu@${{ secrets.EC2_HOST }} << 'ENDSSH'
            cd ~/grocery-management
            git pull origin main
            
            # Create the .env manually or via echo
            echo "DATABASE_URL=${{ secrets.DATABASE_URL }}" > backend/.env
            echo "SECRET_KEY=${{ secrets.SECRET_KEY }}" >> backend/.env
            
            docker compose up -d --build
          ENDSSH

```