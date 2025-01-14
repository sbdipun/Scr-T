export default function handler(req, res) {
  // This function will be triggered when the cron job runs.
  // Add the logic you want to execute (like scraping, sending updates, etc.)
  
  console.log('Cron job executed successfully!');
  res.status(200).end('Cron job executed!');
}
