import { useState, useEffect, useContext } from "react";
import { ErrorContext } from "../contexts/ErrorContext";

const useFetchData = (fetchFunction, setData) => {
  const [isLoading, setIsLoading] = useState(true);
  const { setErrorMessage } = useContext(ErrorContext);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetchFunction();
        setData(response);
      } catch (error) {
        setErrorMessage("A problem occurred. Please try again later.");
      } finally {
        setIsLoading(false);
      }
    };
    fetchData();
  }, [fetchFunction, setErrorMessage]);

  return isLoading;
};

export default useFetchData;
