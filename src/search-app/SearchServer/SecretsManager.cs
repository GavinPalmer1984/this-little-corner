using System;

namespace SearchServer
{
    public class SecretsManager
    {
        public const string ELASTIC_URL = nameof(ELASTIC_URL);
        public const string ELASTIC_USERNAME = nameof(ELASTIC_USERNAME);
        public const string ELASTIC_PASSWORD = nameof(ELASTIC_PASSWORD);
        public const string ELASTIC_CERT = nameof(ELASTIC_CERT);
        public const string OPENAI_API_KEY = nameof(OPENAI_API_KEY);
        public const string YOUTUBE_API_KEY = nameof(YOUTUBE_API_KEY);
        public const string YOUTUBE_SERVICE_ACCOUNT_SECRETS_FILE = nameof(YOUTUBE_SERVICE_ACCOUNT_SECRETS_FILE);
        public const string YOUTUBE_CHANNELS_FROM_ENV = nameof(YOUTUBE_CHANNELS_FROM_ENV);

        public string GetSecret(string name)
        {
            // Try to get the environment variable from Machine, then Process, then User
            string secret = Environment.GetEnvironmentVariable(name, EnvironmentVariableTarget.Machine)
                           ?? Environment.GetEnvironmentVariable(name, EnvironmentVariableTarget.Process)
                           ?? Environment.GetEnvironmentVariable(name, EnvironmentVariableTarget.User);

            if (string.IsNullOrEmpty(secret))
            {
                Console.WriteLine($"Environment variable '{name}' not found.");
                return null;
            }

            return secret;
        }
    }
}
