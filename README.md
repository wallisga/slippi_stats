# Slippi Stats Web Service

A web-based visualization and analysis service for Super Smash Bros. Melee Slippi replay data. This service reads data collected by the Slippi Stats Collector and presents it in an easy-to-use web interface focused on player statistics.

## Overview

The Slippi Stats Web Service provides a player-centric view of gameplay data, allowing players to:

- View overall performance statistics
- Analyze character-specific metrics
- Track matchup data against other players
- See stage performance
- Identify strengths and weaknesses

The service is designed to run alongside the Slippi Stats API Server, reading from the same database but presenting the data in a user-friendly format.

## Features

- **Player Profiles**: Detailed statistics for each player including win rates, character usage, and rival analysis
- **Character Analysis**: Character-specific statistics showing matchup performance and stage preferences
- **Matchup Insights**: Head-to-head statistics between players
- **Interactive Charts**: Visual representation of player performance over time
- **Recent Games**: List of recently played games with results
- **Search Functionality**: Find players by their player code

## Requirements

- Python 3.8+
- Flask
- SQLite3 (shared with the Slippi Stats API Server)
- Web server (Nginx recommended)
- Access to the Slippi Stats database

## Installation

### Option 1: Using the Setup Script

1. Copy the `web_services_setup.sh` script to your server
2. Make it executable:
   ```bash
   chmod +x web_services_setup.sh
   ```
3. Run it as root:
   ```bash
   sudo ./web_services_setup.sh
   ```
4. The script will:
   - Create necessary directories
   - Set up a Python virtual environment
   - Install dependencies
   - Configure Nginx
   - Create a systemd service
   - Set appropriate permissions

### Option 2: Manual Installation

1. Create application directories:
   ```bash
   sudo mkdir -p /opt/slippi-web
   sudo mkdir -p /opt/slippi-web/static/characters
   sudo mkdir -p /opt/slippi-web/static/backgrounds
   sudo mkdir -p /opt/slippi-web/templates
   ```

2. Set up Python environment:
   ```bash
   cd /opt/slippi-web
   python3 -m venv venv
   source venv/bin/activate
   pip install flask gunicorn
   ```

3. Copy the application files:
   - Copy `stats_web_service.py` to `/opt/slippi-web/app.py`
   - Copy template files to `/opt/slippi-web/templates/`
   - Create placeholder images in `/opt/slippi-web/static/`

4. Create Nginx configuration in `/etc/nginx/sites-available/slippi-web`

5. Create systemd service in `/etc/systemd/system/slippi-web.service`

6. Set permissions:
   ```bash
   sudo chown -R slippi:slippi /opt/slippi-web
   sudo chmod -R 755 /opt/slippi-web
   ```

7. Enable and start the service:
   ```bash
   sudo systemctl enable slippi-web
   sudo systemctl start slippi-web
   ```

## Configuration

The web service reads data from the same SQLite database used by the Slippi Stats API Server, located by default at:
```
/opt/slippi-server/app/slippi_data.db
```

If your database is in a different location, you'll need to update the `DATABASE_PATH` variable in the application code.

## Usage

Once installed, you can access the web interface by navigating to your server's IP address in a web browser.

### Main Pages

- **Home Page**: Shows overall stats and recent games
- **Player Profile**: `/player/<player_code>` - Detailed statistics for a specific player
- **Character Stats**: `/character/<player_code>/<character_name>` - Character-specific stats for a player
- **Matchup Analysis**: `/matchup/<player_code>/<opponent_code>` - Head-to-head stats between two players

### API Endpoints

The service also provides JSON API endpoints for more advanced integrations:

- `/api/player/<player_code>/games` - Get a player's games with pagination
- `/api/player/<player_code>/stats` - Get a player's statistics

## Customization

### Character Images

To add character images:
1. Create PNG images named after each character (lowercase with underscores)
2. Place them in `/opt/slippi-web/static/characters/`
3. For example: `/opt/slippi-web/static/characters/fox.png`

### Background Images

For character page background images:
1. Create JPG images named after each character
2. Place them in `/opt/slippi-web/static/backgrounds/`
3. For example: `/opt/slippi-web/static/backgrounds/fox.jpg`

## Maintenance

### Logs

Service logs can be viewed with:
```bash
sudo journalctl -u slippi-web -f
```

Application logs are written to:
```
/opt/slippi-web/stats_server.log
```

### Restarting the Service

If you make changes to the application code:
```bash
sudo systemctl restart slippi-web
```

## Troubleshooting

### Service Won't Start

Check the logs for errors:
```bash
sudo journalctl -u slippi-web -e
```

Common issues include:
- Incorrect database path
- Permission issues
- Port conflicts

### Database Connection Issues

Ensure the web service has read access to the database file:
```bash
sudo chown slippi:slippi /opt/slippi-server/app/slippi_data.db
sudo chmod 644 /opt/slippi-server/app/slippi_data.db
```

### No Data Showing

If the web service runs but doesn't show any data:
1. Check that the API server is running and collecting data
2. Verify the database contains entries
3. Check the path to the database file is correct

## Technical Details

### Database Schema

The web service expects to find the following tables in the SQLite database:

- `clients`: Information about client installations
- `games`: Game data including player information and results

### Performance Considerations

For large databases (10,000+ games), you may want to add indexes to improve query performance:

```sql
CREATE INDEX IF NOT EXISTS idx_games_player_tags ON games(json_extract(player_data, '$[*].player_tag'));
CREATE INDEX IF NOT EXISTS idx_games_start_time ON games(start_time);
```

## Future Improvements