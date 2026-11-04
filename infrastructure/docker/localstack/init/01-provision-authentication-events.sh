#!/bin/bash
set -euo pipefail

region="${AWS_DEFAULT_REGION:-us-east-1}"
bus_name="${AUTHENTICATOR_EVENTBRIDGE_BUS_NAME:-authenticator-bus}"
authentication_bus_name="authentication-bus"
queue_name="${AUTHENTICATOR_EVENTBRIDGE_QUEUE_NAME:-authentication-events}"
rule_name="${AUTHENTICATOR_EVENTBRIDGE_RULE_NAME:-authentication-events-to-sqs}"
account_id="${AUTHENTICATOR_EVENTBRIDGE_ACCOUNT_ID:-000000000000}"

export AWS_DEFAULT_REGION="$region"
export AWS_ACCESS_KEY_ID="${AWS_ACCESS_KEY_ID:-local}"
export AWS_SECRET_ACCESS_KEY="${AWS_SECRET_ACCESS_KEY:-local}"

if ! awslocal events describe-event-bus --name "$bus_name" >/dev/null 2>&1; then
  awslocal events create-event-bus --name "$bus_name" >/dev/null
fi
if ! awslocal events describe-event-bus --name "$authentication_bus_name" >/dev/null 2>&1; then
  awslocal events create-event-bus --name "$authentication_bus_name" >/dev/null
fi
queue_url="$(awslocal sqs create-queue --queue-name "$queue_name" --query QueueUrl --output text)"
queue_arn="$(awslocal sqs get-queue-attributes --queue-url "$queue_url" \
  --attribute-names QueueArn --query 'Attributes.QueueArn' --output text)"

awslocal events put-rule \
  --name "$rule_name" \
  --event-bus-name "$bus_name" \
  --event-pattern '{"detail-type":["authentication.authentication.succeeded","authentication.authentication.failed","authentication.session.created","authentication.session.terminated"]}' \
  --state ENABLED >/dev/null

awslocal events put-targets \
  --event-bus-name "$bus_name" \
  --rule "$rule_name" \
  --targets "Id=authentication-events-sqs,Arn=$queue_arn" >/dev/null

awslocal events put-rule \
  --name "$rule_name" \
  --event-bus-name "$authentication_bus_name" \
  --event-pattern '{"detail-type":["authentication.authentication.succeeded","authentication.authentication.failed","authentication.session.created","authentication.session.terminated"]}' \
  --state ENABLED >/dev/null

awslocal events put-targets \
  --event-bus-name "$authentication_bus_name" \
  --rule "$rule_name" \
  --targets "Id=authentication-events-sqs,Arn=$queue_arn" >/dev/null

awslocal sqs set-queue-attributes \
  --queue-url "$queue_url" \
  --attributes "{\"Policy\":\"{\\\"Version\\\":\\\"2012-10-17\\\",\\\"Statement\\\":[{\\\"Sid\\\":\\\"AllowEventBridge\\\",\\\"Effect\\\":\\\"Allow\\\",\\\"Principal\\\":{\\\"Service\\\":\\\"events.amazonaws.com\\\"},\\\"Action\\\":\\\"sqs:SendMessage\\\",\\\"Resource\\\":\\\"$queue_arn\\\",\\\"Condition\\\":{\\\"ArnEquals\\\":{\\\"aws:SourceArn\\\":\\\"arn:aws:events:$region:$account_id:rule/$bus_name/$rule_name\\\"}}}]}\"}" \
  >/dev/null

echo "LocalStack provisioned EventBridge bus '$bus_name', rule '$rule_name', and queue '$queue_name'."
