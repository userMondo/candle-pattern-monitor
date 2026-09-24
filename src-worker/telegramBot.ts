/**
 * Telegram Bot API client for Cloudflare Workers.
 * Uses fetch API (available in Workers runtime).
 */
export class TelegramBot {
  private readonly token: string;
  private readonly chatId: string;

  constructor(token: string, chatId: string) {
    this.token = token;
    this.chatId = chatId;
  }

  async sendMessage(text: string, parseMode: string = 'Markdown'): Promise<boolean> {
    if (!this.token || !this.chatId) {
      console.error('[TelegramBot] Token or chat ID not configured');
      return false;
    }

    try {
      const url = `https://api.telegram.org/bot${this.token}/sendMessage`;
      const resp = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          chat_id: this.chatId,
          text,
          parse_mode: parseMode,
          disable_web_page_preview: false,
        }),
      });

      if (!resp.ok) {
        const body = await resp.text();
        console.error(`[TelegramBot] Failed to send message: ${resp.status} ${body}`);
        return false;
      }

      return true;
    } catch (e) {
      console.error('[TelegramBot] Error:', e);
      return false;
    }
  }
}
