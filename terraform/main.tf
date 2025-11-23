provider "aws" {
  region = var.aws_region
}

data "aws_caller_identity" "current" {}

resource "aws_sqs_queue" "main" {
  name                        = "notifications-queue.fifo"
  fifo_queue                  = true
  content_based_deduplication = true
  visibility_timeout_seconds  = 60
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.dlq.arn
    maxReceiveCount     = 5
  })
}

resource "aws_sqs_queue" "dlq" {
  name       = "notifications-dlq.fifo"
  fifo_queue = true
}

resource "aws_dynamodb_table" "notifications" {
  name         = "Notifications"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "message_id"

  attribute {
    name = "message_id"
    type = "S"
  }
}

resource "aws_sns_topic" "notifications" {
  name = "notification-events"
}

resource "aws_iam_role" "lambda_role" {
  name = "notification_lambda_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_basic" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
  role       = aws_iam_role.lambda_role.name
}

resource "aws_iam_role_policy" "lambda_sqs_dynamo" {
  name = "lambda_sqs_dynamo_policy"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "sqs:ReceiveMessage",
          "sqs:DeleteMessage",
          "sqs:GetQueueAttributes",
          "sqs:SendMessage"
        ]
        Resource = [aws_sqs_queue.main.arn, aws_sqs_queue.dlq.arn]
      },
      {
        Effect = "Allow"
        Action = [
          "dynamodb:PutItem",
          "dynamodb:GetItem",
          "dynamodb:UpdateItem"
        ]
        Resource = aws_dynamodb_table.notifications.arn
      },
      {
        Effect = "Allow"
        Action = "sns:Publish"
        Resource = aws_sns_topic.notifications.arn
      }
    ]
  })
}

resource "aws_lambda_function" "worker" {
  filename         = "lambda_function_payload.zip"
  function_name    = "notification-worker"
  role             = aws_iam_role.lambda_role.arn
  handler          = "worker.lambda_handler"
  source_code_hash = filebase64sha256("lambda_function_payload.zip")
  runtime          = "python3.9"

  environment {
    variables = {
      DYNAMODB_TABLE = aws_dynamodb_table.notifications.name
      QUEUE_URL      = aws_sqs_queue.main.id
      SNS_TOPIC_ARN  = aws_sns_topic.notifications.arn
    }
  }
}
