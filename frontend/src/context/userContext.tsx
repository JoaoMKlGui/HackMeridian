"use client";

import {
  allowAllModules,
  FREIGHTER_ID,
  ISupportedWallet,
  StellarWalletsKit,
  WalletNetwork,
} from "@creit.tech/stellar-wallets-kit";
import { LedgerModule } from "@creit.tech/stellar-wallets-kit/modules/ledger.module";
import {
  WalletConnectAllowedMethods,
  WalletConnectModule,
} from "@creit.tech/stellar-wallets-kit/modules/walletconnect.module";
import {
  createContext,
  ReactNode,
  useContext,
  useEffect,
  useRef,
  useState,
} from "react";

interface UserContextProps {
  address: string | null;
  setAddress: (address: string | null) => void;
  kit: StellarWalletsKit | null;
  connectWallet: () => Promise<void>;
  disconnect: () => void;
  signTransaction: (xdr: string, userAddress: string) => Promise<string>;
}

interface UserProviderProps {
  children: ReactNode;
}

export const UserProvider = ({ children }: UserProviderProps) => {
  const [address, setAddress] = useState<string | null>(null);
  const [kit, setKit] = useState<StellarWalletsKit | null>(null);
  const kitRef = useRef<StellarWalletsKit | null>(null);

  useEffect(() => {
    if (typeof window !== "undefined" && !kitRef.current) {
      try {
        const walletKit = new StellarWalletsKit({
          network: WalletNetwork.PUBLIC,
          selectedWalletId: FREIGHTER_ID,
          modules: [
            ...[...allowAllModules(), new LedgerModule()],
            new WalletConnectModule({
              url:
                typeof window !== "undefined"
                  ? window.location.origin
                  : "http://localhost:3000",
              projectId: "da8bdbbdeb3119b9d2e37ec8aff1789a",
              method: WalletConnectAllowedMethods.SIGN,
              description: `Example`,
              name: "Example",
              icons: ["/walletconnect.svg"],
              network: WalletNetwork.PUBLIC,
            }),
          ],
        });
        kitRef.current = walletKit;
        setKit(walletKit);
      } catch (error) {
        console.error("Failed to initialize wallet kit:", error);
      }
    }
  }, []);

  const connectWallet = async () => {
    if (!kit) return;

    await kit.openModal({
      onWalletSelected: async (option: ISupportedWallet) => {
        kit.setWallet(option.id);
        const { address } = await kit.getAddress();
        setAddress(address);
      },
    });
  };

  const disconnect = () => {
    if (kit) {
      kit.disconnect();
      setAddress(null);
    }
  };

  const signTransaction = async (
    xdr: string,
    userAddress: string
  ): Promise<string> => {
    console.log("🚀 | signTransaction | userAddress:", userAddress);
    if (!kit) throw new Error("Wallet kit not initialized");

    const { signedTxXdr } = await kit.signTransaction(xdr, {
      address: userAddress,
      networkPassphrase: WalletNetwork.PUBLIC,
    });

    if (!signedTxXdr) throw new Error("Failed to sign transaction");
    return signedTxXdr;
  };

  return (
    <UserContext.Provider
      value={{
        setAddress,
        address,
        kit,
        connectWallet,
        disconnect,
        signTransaction,
      }}
    >
      {children}
    </UserContext.Provider>
  );
};

export const UserContext = createContext<UserContextProps>({
  address: null,
  setAddress: () => {},
  kit: null,
  connectWallet: async () => {},
  disconnect: () => {},
  signTransaction: async () => "",
});

export const useUserContext = () => useContext(UserContext);
