import { useContext, useEffect, useState } from "react";

import { AlertContext } from "../contexts/AlertContext";

const useFetchData = (fetchFunction, setData, dependencies) => {
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
  }, dependencies);

  return isLoading;
};

export default useFetchData;
