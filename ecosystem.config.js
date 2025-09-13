module.exports = {
  apps: [{
    name: 'instagram-analyzer',
    script: 'app.py',
    interpreter: 'python3',
    cwd: '/home/user/webapp',
    instances: 1,
    exec_mode: 'fork',
    watch: false,
    env: {
      NODE_ENV: 'production',
      PORT: 5000,
      FLASK_DEBUG: false
    },
    env_development: {
      NODE_ENV: 'development',
      PORT: 5000,
      FLASK_DEBUG: true
    },
    log_file: '/home/user/webapp/logs/combined.log',
    out_file: '/home/user/webapp/logs/out.log',
    error_file: '/home/user/webapp/logs/error.log',
    pid_file: '/home/user/webapp/logs/pid',
    max_memory_restart: '1G',
    restart_delay: 4000,
    autorestart: true
  }]
}