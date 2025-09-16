
export default function DashboardPage() {
  const scoreboard = [
    "Player1",
    "Player2",
    "Player3",
    "Player4",
    "Player5",
  ];
  const currentStatus = "In Progress";

  return (
    <main className="flex min-h-screen flex-col items-center p-24">
      <h1 className="mb-8 text-4xl font-bold">
        <span className="bg-gradient-to-r from-pink-500 to-blue-500 bg-clip-text text-transparent">
          Active Members
        </span>
      </h1>
      <div className="flex w-full max-w-4xl flex-row justify-center gap-16">
        <div className="w-full max-w-md">
          <ul className="space-y-4">
            {scoreboard.map((user, index) => (
              <li
                key={index}
                className="flex items-center justify-between rounded-lg bg-white/50 p-4 shadow-md backdrop-blur-lg"
              >
                <span className="text-lg font-semibold text-gray-700">
                  {index + 1}. {user}
                </span>
              </li>
            ))}
          </ul>
        </div>
        <div className="mt-2">
          <h2 className="text-2xl font-bold text-gray-700">Status:</h2>
          <p className="mt-2 text-xl text-gray-600">{currentStatus}</p>
        </div>
      </div>
    </main>
  );
}
