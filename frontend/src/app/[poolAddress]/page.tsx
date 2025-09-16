"use client";

import { useParams } from "next/navigation";

export default function PoolPage() {
  const params = useParams();
  return (
    <main className="mt-[100px] flex min-h-[calc(100vh-100px)] justify-center p-2">
      <div className="flex flex-col items-center justify-center">
        <p>UserName: </p>
        <p>Pool Address: {params.poolAddress}</p>
        <p>Competition: XXXXX</p>
      </div>
    </main>
  );
}
