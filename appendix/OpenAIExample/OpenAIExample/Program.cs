using System;
using OpenAI.Chat;

class Program
{
    static void Main(string[] args)
    {
        var apiKey = Environment.GetEnvironmentVariable("OPENAI_API_KEY");
        var chatClient = new ChatClient("gpt-4o-mini", apiKey);

        Console.WriteLine("OpenAI 채팅봇과 대화를 시작합니다. 종료하려면 'quit'을 입력하세요.");

        while (true)
        {
            Console.Write("You: ");
            var userInput = Console.ReadLine();

            if (userInput?.ToLower() == "quit")
                break;

            try
            {
                var messages = new[] { new UserChatMessage(userInput) };
                var completion = chatClient.CompleteChat(messages);

                Console.WriteLine($"AI: {completion.Value.Content[0].Text}");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"오류 발생: {ex.Message}");
            }
        }

        Console.WriteLine("대화를 종료합니다.");
    }
}
