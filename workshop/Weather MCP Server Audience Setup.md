# Weather MCP Server - Audience Setup (Quick Guide)

Use this when demonstrating how attendees add the weather server to their Copilot Studio agent.

## Connector Values

- modelDisplayName: Weather MCP Server
- modelDescription: Provides real-time weather and short-range forecast data for warehouse locations using city, ZIP, or place name inputs. Use it to support shift planning, heat safety checks, and weather-related operational decisions across CA, NV, and AZ facilities.
- operationId: invoke
- action kind: InvokeExternalAgentTaskAction

## URL To Use

Primary endpoint URL:

https://YOUR_APP_NAME.YOUR_ENVIRONMENT.YOUR_REGION.azurecontainerapps.io/mcp/

If a client asks for base URL instead of endpoint path, use:

https://YOUR_APP_NAME.YOUR_ENVIRONMENT.YOUR_REGION.azurecontainerapps.io

## Minimal Action Template

```yaml
action:
  kind: InvokeExternalAgentTaskAction
  connectionProperties:
    mode: Invoker
  operationDetails:
    kind: ModelContextProtocolMetadata
    operationId: invoke
    tools:
      kind: UseAllTools
```

## 60-Second Walkthrough Script

1. Open the agent tool/action setup in Copilot Studio.
2. Enter the display name and description exactly as provided above.
3. Paste the endpoint URL ending in /mcp/.
4. Confirm operationId is invoke.
5. Save and run a quick test prompt such as: "What is tomorrow's weather in Phoenix, AZ, and how should daytime shifts be adjusted?"

## Quick Validation

- Tool call returns weather data for at least one AZ location.
- Agent answer includes weather-grounded recommendations for shift planning and heat safety.
- No manual tool mention is required in the user prompt.
