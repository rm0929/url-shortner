const { SQSClient, ReceiveMessageCommand, DeleteMessageCommand } = require("@aws-sdk/client-sqs");
const { initDB, recordClick } = require("../services/db");

const sqsClient = new SQSClient({
  region: process.env.AWS_DEFAULT_REGION || "us-east-1",
  credentials: {
    accessKeyId: process.env.AWS_ACCESS_KEY_ID || "test",
    secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY || "test",
  },
  // LocalStack endpoint for local dev; remove for real AWS
  ...(process.env.AWS_ENDPOINT_URL && {
    endpoint: process.env.AWS_ENDPOINT_URL,
  }),
});

const QUEUE_URL = process.env.SQS_QUEUE_URL;

async function processMessage(message) {
  const body = JSON.parse(message.Body);
  console.log(`[consumer] Processing click for: ${body.short_code}`);

  await recordClick({
    short_code: body.short_code,
    timestamp: body.timestamp,
    cache_hit: body.cache_hit ?? false,
  });
}

async function pollQueue() {
  const command = new ReceiveMessageCommand({
    QueueUrl: QUEUE_URL,
    MaxNumberOfMessages: 10,      // Batch up to 10 messages per poll
    WaitTimeSeconds: 20,           // Long polling — reduces empty receives
  });

  const response = await sqsClient.send(command);
  const messages = response.Messages || [];

  for (const message of messages) {
    try {
      await processMessage(message);

      // Delete from queue only after successful processing
      await sqsClient.send(
        new DeleteMessageCommand({
          QueueUrl: QUEUE_URL,
          ReceiptHandle: message.ReceiptHandle,
        })
      );
    } catch (err) {
      // Log but don't delete — message becomes visible again after visibility timeout
      console.error(`[consumer] Failed to process message: ${err.message}`);
    }
  }

  return messages.length;
}

async function startConsumer() {
  await initDB();
  console.log("[consumer] Starting SQS consumer loop...");

  while (true) {
    try {
      const count = await pollQueue();
      if (count > 0) {
        console.log(`[consumer] Processed ${count} messages`);
      }
    } catch (err) {
      console.error("[consumer] Poll error:", err.message);
      // Back off before retrying on error
      await new Promise((resolve) => setTimeout(resolve, 5000));
    }
  }
}

module.exports = { startConsumer };
