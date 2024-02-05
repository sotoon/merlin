import { useState, useEffect, useContext } from "react";
import { AlertContext } from "../contexts/AlertContext";

const useFetchData = (fetchFunction, setData) => {
  const [isLoading, setIsLoading] = useState(true);
  const { setAlert } = useContext(AlertContext);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetchFunction();
        setData(response);
      } catch (error) {
        setAlert({
          message: "A problem occurred. Please try again later.",
          type: "error",
        });
      } finally {
        setIsLoading(false);
      }
    };
    fetchData();
  }, [fetchFunction, setAlert]);

  return isLoading;
};

export default useFetchData;
