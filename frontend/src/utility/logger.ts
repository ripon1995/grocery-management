export class Logger {
    private readonly context: string;
  constructor(context: string = "App") {
      this.context = context;
  }

  info(message: string, ...data: never[]) {
    console.log(`%c[${this.context}] [INFO]`, "color: #007acc; font-weight: bold;", message, ...data);
  }

  warn(message: string, ...data: never[]) {
    console.warn(`%c[${this.context}] [WARN]`, "color: #e6a23c; font-weight: bold;", message, ...data);
  }

  error(message: string, ...data: never[]) {
    console.error(`%c[${this.context}] [ERROR]`, "color: #f56c6c; font-weight: bold;", message, ...data);
  }
}