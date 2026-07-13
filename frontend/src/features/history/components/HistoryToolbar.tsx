import Button from "../../../components/ui/Button";
import Input from "../../../components/ui/Input";

import {

    RefreshCw,

} from "lucide-react";

interface Props {

    search: string;

    onSearch: (value: string) => void;

    onRefresh: () => void;

}

export default function HistoryToolbar({

    search,

    onSearch,

    onRefresh,

}: Props) {

    return (

        <div
            className="
                flex
                flex-col
                lg:flex-row
                gap-4
                justify-between
                items-center
            "
        >

            <Input

                placeholder="Search filename..."

                value={search}

                onChange={(e)=>

                    onSearch(

                        e.target.value,

                    )

                }

            />

            <Button

                onClick={onRefresh}

            >

                <RefreshCw

                    size={18}

                />

                Refresh

            </Button>

        </div>

    );

}