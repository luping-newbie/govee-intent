# opentelemetry 配置
# 1. Azure portal 上创建trace 信息搜集的资源，获取 connection_string: https://learn.microsoft.com/en-us/azure/ai-foundry/how-to/develop/trace-application
# 2. 安装相关的Python lib: pip install azure-ai-projects azure-monitor-opentelemetry opentelemetry-instrumentation-openai-v2
# 3. 默认会生成一些span，如果需要更多和业务相关的span，可以通过 @tracer.start_as_current_span(span_name)自定义
import os
from opentelemetry.instrumentation.openai_v2 import OpenAIInstrumentor
from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry import trace
from dotenv import load_dotenv


load_dotenv()
def init_trace_config(connection_string: str, trace_name = "govee-knowledge")-> trace.Tracer:
    os.environ["OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT"]="true"
    OpenAIInstrumentor().instrument()
    configure_azure_monitor(connection_string=connection_string)
    tracer = trace.get_tracer(instrumenting_module_name=trace_name)
    return tracer
