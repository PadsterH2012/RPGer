#!/bin/bash
# Setup Backup Cron Job Script for RPGer
# This script sets up a cron job to run the database backup script automatically

# Set colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKUP_SCRIPT="${SCRIPT_DIR}/backup_db.sh"

echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}   RPGer Backup Cron Job Setup          ${NC}"
echo -e "${BLUE}=========================================${NC}"

# Check if backup script exists
if [ ! -f "$BACKUP_SCRIPT" ]; then
    echo -e "${RED}Backup script not found: ${BACKUP_SCRIPT}${NC}"
    exit 1
fi

# Make sure backup script is executable
chmod +x "$BACKUP_SCRIPT"

# Prompt for backup frequency
echo -e "\n${BLUE}Select backup frequency:${NC}"
echo "1. Daily (at midnight)"
echo "2. Weekly (Sunday at midnight)"
echo "3. Custom schedule"
read -p "Enter your choice (1-3): " frequency_choice

case $frequency_choice in
    1)
        # Daily at midnight
        CRON_SCHEDULE="0 0 * * *"
        FREQUENCY_DESC="daily at midnight"
        ;;
    2)
        # Weekly on Sunday at midnight
        CRON_SCHEDULE="0 0 * * 0"
        FREQUENCY_DESC="weekly on Sunday at midnight"
        ;;
    3)
        # Custom schedule
        echo -e "\n${BLUE}Enter custom cron schedule:${NC}"
        echo "Format: minute hour day month weekday"
        echo "Example: 0 0 * * * (daily at midnight)"
        read -p "Cron schedule: " CRON_SCHEDULE
        FREQUENCY_DESC="custom schedule: $CRON_SCHEDULE"
        ;;
    *)
        echo -e "${RED}Invalid choice. Exiting.${NC}"
        exit 1
        ;;
esac

# Create log directory
LOG_DIR="${PROJECT_ROOT}/logs"
mkdir -p "$LOG_DIR"

# Create cron job
CRON_JOB="${CRON_SCHEDULE} ${BACKUP_SCRIPT} >> ${LOG_DIR}/backup.log 2>&1"

# Check if crontab is available
if ! command -v crontab > /dev/null; then
    echo -e "${RED}crontab command not found. Please install cron.${NC}"
    exit 1
fi

# Check if the cron job already exists
EXISTING_CRON=$(crontab -l 2>/dev/null | grep -F "$BACKUP_SCRIPT")

if [ -n "$EXISTING_CRON" ]; then
    echo -e "${YELLOW}A cron job for the backup script already exists:${NC}"
    echo "$EXISTING_CRON"
    read -p "Do you want to replace it? (y/n): " replace_cron
    
    if [ "$replace_cron" != "y" ]; then
        echo -e "${YELLOW}Cron job setup cancelled.${NC}"
        exit 0
    fi
    
    # Remove existing cron job
    crontab -l 2>/dev/null | grep -v -F "$BACKUP_SCRIPT" | crontab -
fi

# Add new cron job
(crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -

if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}Cron job set up successfully!${NC}"
    echo -e "Backup will run ${FREQUENCY_DESC}"
    echo -e "Backup logs will be saved to: ${LOG_DIR}/backup.log"
    
    # Show current crontab
    echo -e "\n${BLUE}Current crontab:${NC}"
    crontab -l
else
    echo -e "\n${RED}Failed to set up cron job.${NC}"
    exit 1
fi

echo -e "\n${BLUE}To manually run a backup, use:${NC}"
echo -e "  ${BACKUP_SCRIPT}"

echo -e "\n${BLUE}To restore from a backup, use:${NC}"
echo -e "  ${SCRIPT_DIR}/restore_db.sh"

exit 0
